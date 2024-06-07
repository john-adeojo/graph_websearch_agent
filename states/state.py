from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# Define the state object for the agent graph
class AgentGraphState(TypedDict):
    research_question: str
    planner_response: Annotated[list, add_messages]
    researcher_response: Annotated[list, add_messages]
    reporter_response: Annotated[list, add_messages]
    reviewer_response: Annotated[list, add_messages]
    serper_response: Annotated[list, add_messages]
    scraper_response: Annotated[list, add_messages]
    end_chain: Annotated[list, add_messages]

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
    "research_question":"",
    "planner_response": [],
    "researcher_response": [],
    "reporter_response": [],
    "reviewer_response": [],
    "serper_response": [],
    "scraper_response": [],
    "end_chain": ""
}