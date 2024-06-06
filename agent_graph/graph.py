import ast
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

from models.openai_models import get_open_ai_json
from agents.agents import planner_agent, researcher_agent, reporter_agent, reviewer_agent

# Define the state object for the agent graph
class AgentGraphState(TypedDict):
    input: str
    planner: Annotated[list, add_messages]
    researcher: Annotated[list, add_messages]
    reporter: Annotated[list, add_messages]
    reviewer: Annotated[list, add_messages]
    research: Annotated[list, add_messages]

# Define the nodes in the agent graph
graph = StateGraph(AgentGraphState)

def get_agent_graph_state(state:AgentGraphState, agent:str):
    if agent == "planner":
        return planner_agent(state["planner"])
    elif agent == "researcher":
        return researcher_agent(state["researcher"])
    elif agent == "reporter":
        return reporter_agent(state["reporter"])
    elif agent == "reviewer_all":
        return reviewer_agent(state["reviewer"])
    elif agent == "reviewer_latest":
        return reviewer_agent(state["reviewer"][-1])
    else:
        return None
    
graph.add_node(
    "planner", 
    planner_agent(
        feedback=get_agent_graph_state(agent="reviewer_latest"),
        previous_plans=get_agent_graph_state(agent="planner")
    )
)
graph.add_node(
    "researcher",
    researcher_agent(
        feedback=get_agent_graph_state(agent="reviewer_latest"),
        previous_selections=get_agent_graph_state(agent="researcher")
    )
)
graph.add_node(
    "reporter", 
    reporter_agent(
        feedback=get_agent_graph_state(agent="reviewer_latest"),
        previous_reports=get_agent_graph_state(agent="reporter")
    )
)

graph.add_node(
    "reviewer", 
    reviewer_agent(
        feedback=get_agent_graph_state(agent="reviewer_all"),
        planner=get_agent_graph_state(agent="planner"),
        researcher=get_agent_graph_state(agent="researcher"),
        reporter=get_agent_graph_state(agent="reporter")
    )
)

graph.add_node("websearch_tool", {})
graph.add_node("end", END)

# Define the edges in the agent graph
def pass_review(state: AgentGraphState, llm=get_open_ai_json):
    review_list =  state["reviewer"]
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

      

    