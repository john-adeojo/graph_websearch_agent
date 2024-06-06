import ast
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from models.openai_models import get_open_ai_json
from agents.agents import planner_agent, researcher_agent, reporter_agent, reviewer_agent
from tools.google_serper import get_google_serper
from tools.basic_scraper import scrape_website

# Define the state object for the agent graph
class AgentGraphState(TypedDict):
    planner_response: Annotated[list, add_messages]
    researcher_response: Annotated[list, add_messages]
    reporter_response: Annotated[list, add_messages]
    reviewer_response: Annotated[list, add_messages]
    serper_response: Annotated[list, add_messages]
    scraper_response: Annotated[list, add_messages]
    end_chain: str

# Define the nodes in the agent graph
def get_agent_graph_state(state:AgentGraphState, state_key:str):
    if state_key == "planner_all":
        return state["planner_response"]
    elif state_key == "planner_latest":
        if state["planner_response"]:
            return state["planner_response"][-1]
        else:
            return state["planner_response"]
    
    elif state_key == "researcher_all":
        return state["researcher_response"]
    elif state_key == "researcher_latest":
        if state["researcher_response"]:
            return state["researcher_response"][-1]
        else:
            return state["researcher_response"]
    
    elif state_key == "reporter_all":
        return state["reporter_response"]
    elif state_key == "reporter_latest":
        if state["reporter_response"]:
            return state["reporter_response"][-1]
        else:
            return state["reporter_response"]
    
    elif state_key == "reviewer_all":
        return state["reviewer_response"]
    elif state_key == "reviewer_latest":
        if state["reviewer_response"]:
            return state["reviewer_response"][-1]
        else:
            return state["reviewer_response"]
        
    elif state_key == "serper_all":
        return state["serper_response"]
    elif state_key == "serper_latest":
        if state["serper_response"]:
            return state["serper_response"][-1]
        else:
            return state["serper_response"]
    
    elif state_key == "scraper_all":
        return state["scraper_response"]
    elif state_key == "scraper_latest":
        if state["scraper_response"]:
            return state["scraper_response"][-1]
        else:
            return state["scraper_response"]
        
    else:
        return None
    
state = {
    "planner_response": [], 
    "researcher_response": [], 
    "reporter_response": [], 
    "reviewer_response": [], 
    "researcher_response": [],
    "serper_response": [],
    "scraper_response": [],
    "end_chain": []
}

graph = StateGraph(AgentGraphState)
   
graph.add_node(
    "planner", 
    lambda state: {"planner_response": add_messages(
        planner_agent(
        feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
        previous_plans=lambda: get_agent_graph_state(state=state, state_key="planner_all")
        )
    )}
)
graph.add_node(
    "researcher",
    lambda state: {"researcher_response": add_messages(
        researcher_agent(
        feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
        previous_selections=lambda: get_agent_graph_state(state=state, state_key="researcher_all"),
        serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest")
        )
    )}
)
graph.add_node(
    "reporter", 
    lambda state: {"reporter_response": add_messages(
        reporter_agent(
        feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"),
        previous_reports=lambda: get_agent_graph_state(state=state, state_key="reporter_all"),
        research=lambda: get_agent_graph_state(state=state, state_key="researcher_latest")
        )
    )}
)

graph.add_node(
    "reviewer", 
    lambda state: {"reviewer_response": add_messages(
        reviewer_agent(
        feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_all"),
        planner=lambda: get_agent_graph_state(state=state, state_key="planner_latest"),
        researcher=lambda: get_agent_graph_state(state=state, state_key="researcher_latest"),
        reporter=lambda: get_agent_graph_state(state=state, state_key="reporter_latest")
        )
    )}
)

graph.add_node(
    "serper_tool",
    lambda state: {"serper_response": add_messages( 
        get_google_serper(
        plan=lambda: get_agent_graph_state(state=state, state_key="planner_latest")
        )
    )}
)

graph.add_node(
    "scraper_tool",
    lambda state: {"scraper_response": add_messages(
        scrape_website(
        research=lambda: get_agent_graph_state(state=state, state_key="researcher_latest")
        )
    )}
)

graph.add_node("end", lambda state: {"end_chain": "end"})


# Define the edges in the agent graph
def pass_review(state: AgentGraphState, llm=get_open_ai_json):
    review_list =  state["reviewer_response"]
    if review_list:
        review = review_list[-1]
    else:
        review = "No review"

    messages = [
        (
            "system",
            """
            Your purpose is to route the conversation to the appropriate agent based on the reviewer's feedback.
            You do this by providing a response in the form of a dictionary.
            For the first key, "review_pass", you must provide a value of "True" or "False".
            If the reviewer approves, return True. Otherwise, return False.

            For the second key, "next_agent", you must provide the name of the agent to route the conversation to.
            Your choices are: planner, researcher, reporter, or end.
            You must select only ONE of these options.
            
            Your response must be a dictionary with this format:
            {
                "review_pass": "True/False",
                "next_agent": "planner/researcher/reporter/end"
            }   
            """
        ),
        ("reviewer", f"Reviewer's feedback: {review}")
    ]

    ai_msg = llm.invoke(messages)

    review_dict = ast.literal_eval(ai_msg.content)

    # To hanbdle abnormally formatted responses
    try:
        next_agent = review_dict["next_agent"]
        print (f"Review Passed: {review_dict['review_pass']}\n\n Handing over to {next_agent}\n")

    except KeyError as e:
        next_agent = "end"
        print (f"Error: {e}\n\n Exiting agent flow {next_agent}\n")

    return next_agent

# Add edges to the graph

graph.set_entry_point("planner")
graph.set_finish_point("end")
graph.add_edge("planner", "serper_tool")
graph.add_edge("serper_tool", "researcher")
graph.add_edge("researcher", "scraper_tool")
graph.add_edge("scraper_tool", "reporter")
graph.add_edge("reporter", "reviewer")

graph.add_conditional_edges(
    "reviewer",
    pass_review,

)

workflow = graph.compile()

if __name__ == "__main__":
    inputs = {"messages": [HumanMessage(content="what is the weather in sf")]}
    workflow.invoke(inputs)