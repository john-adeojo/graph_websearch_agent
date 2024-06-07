import ast
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage
from models.openai_models import get_open_ai_json
from langgraph.checkpoint.sqlite import SqliteSaver
from agents.agents import (
    planner_agent, 
    researcher_agent, 
    reporter_agent, 
    reviewer_agent, 
    final_report, 
    end_node
    )
from prompts.prompts import (
    reviewer_prompt_template, 
    planner_prompt_template, 
    researcher_prompt_template, 
    reporter_prompt_template
    )
from tools.google_serper import get_google_serper
from tools.basic_scraper import scrape_website
from states.state import AgentGraphState, get_agent_graph_state, state

graph = StateGraph(AgentGraphState)

graph.add_node(
    "planner", 
    lambda state: planner_agent(
        state=state,
        research_question=state["research_question"],  
        feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"), 
        previous_plans=lambda: get_agent_graph_state(state=state, state_key="planner_all")
    )
)

graph.add_node(
    "researcher",
    lambda state: researcher_agent(
        state=state,
        research_question=state["research_question"], 
        feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"), 
        previous_selections=lambda: get_agent_graph_state(state=state, state_key="researcher_all"), 
        serp=lambda: get_agent_graph_state(state=state, state_key="serper_latest")
    )
)

graph.add_node(
    "reporter", 
    lambda state: reporter_agent(
        state=state,
        research_question=state["research_question"], 
        feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_latest"), 
        previous_reports=lambda: get_agent_graph_state(state=state, state_key="reporter_all"), 
        research=lambda: get_agent_graph_state(state=state, state_key="researcher_latest")
    )
)

graph.add_node(
    "reviewer", 
    lambda state: reviewer_agent(
        state=state,
        research_question=state["research_question"], 
        feedback=lambda: get_agent_graph_state(state=state, state_key="reviewer_all"), 
        planner=lambda: get_agent_graph_state(state=state, state_key="planner_latest"), 
        researcher=lambda: get_agent_graph_state(state=state, state_key="researcher_latest"), 
        reporter=lambda: get_agent_graph_state(state=state, state_key="reporter_latest"),
        planner_agent=planner_prompt_template,
        researcher_agent=researcher_prompt_template,
        reporter_agent=reporter_prompt_template,
    )
)

graph.add_node(
    "serper_tool",
    lambda state: get_google_serper(
        state=state,
        plan=lambda: get_agent_graph_state(state=state, state_key="planner_latest")
    )
)

graph.add_node(
    "scraper_tool",
    lambda state: scrape_website(
        state=state,
        research=lambda: get_agent_graph_state(state=state, state_key="researcher_latest")
    )
)

graph.add_node(
    "final_report", 
    lambda state: final_report(
        state=state,
        final_response=lambda: get_agent_graph_state(state=state, state_key="reporter_latest")
        )
)

graph.add_node("end", lambda state: end_node(state=state))

# Define the edges in the agent graph
def pass_review(state: AgentGraphState, llm=get_open_ai_json()):
    review_list = state["reviewer_response"]
    if review_list:
        review = review_list[-1]
    else:
        review = "No review"

    messages = [
        {
            "role":"system","content":
            """
            Your purpose is to route the conversation to the appropriate agent based on the reviewer's feedback.
            You do this by providing a response in the form of a dictionary.
            For the first key, "review_pass", you must provide a value of "True" or "False".
            If the reviewer approves, return True. Otherwise, return False.

            For the second key, "next_agent", you must provide the name of the agent to route the conversation to.
            Your choices are: planner, researcher, reporter, or final_report.
            You must select only ONE of these options.

            Your response must be a json:
            {
                "review_pass": "True/False",
                "next_agent": "planner/researcher/reporter/final_report"
            }
            """
        },
        {"role":"user", "content": f"Reviewer's feedback: {review}. Respond with json"}
    ]

    ai_msg = llm.invoke(messages)

    review_dict = ast.literal_eval(ai_msg.content)

    # To handle abnormally formatted responses
    try:
        next_agent = review_dict["next_agent"]
        print(f"Review Passed: {review_dict['review_pass']}\n\n Handing over to {next_agent}\n")

    except KeyError as e:
        next_agent = "end"
        print(f"Error: {e}\n\n Exiting agent flow {next_agent}\n")

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
    lambda state: pass_review(state=state)
)

graph.add_edge("final_report", "end")

# workflow = graph.compile()
memory = SqliteSaver.from_conn_string(":memory:")  # Here we only save in-memory
workflow = graph.compile(checkpointer=memory, interrupt_before=["end"])

if __name__ == "__main__":

    question = "When did the capital of Nigeria change?"
    inputs = {"research_question": question}
    # workflow.invoke(inputs)

    verbose = False

    # Run the graph
    thread = {"configurable": {"thread_id": "4"}}
    for event in workflow.stream(inputs, thread, stream_mode="values"):
        if verbose:
            print("\n\n\nEVENT", event)
        else:
            print("\n\n")