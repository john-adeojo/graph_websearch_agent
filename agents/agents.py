import yaml
import os
from models.openai_models import get_open_ai, get_open_ai_json
from prompts.prompts import (
    planner_prompt_template,
    researcher_prompt_template,
    reporter_prompt_template,
    reviewer_prompt_template
)
from utils.helper_functions import get_current_utc_datetime
from states.state import AgentGraphState


def planner_agent(state:AgentGraphState, research_question, prompt=planner_prompt_template, llm=get_open_ai_json(), feedback=None, previous_plans=None):

    feedback_value = feedback() if callable(feedback) else feedback
    previous_plans_value = previous_plans() if callable(previous_plans) else previous_plans

    planner_prompt = prompt.format(
        feedback=feedback_value,
        previous_plans=previous_plans_value,
        datetime=get_current_utc_datetime()
    )

    messages = [
        {"role": "system", "content": planner_prompt},
        {"role": "human", "content": f"research question: {research_question}"}
    ]

    ai_msg = llm.invoke(messages)

    state = {**state, "planner_response": ai_msg.content}

    return state

def researcher_agent(state:AgentGraphState, research_question, prompt=researcher_prompt_template, llm=get_open_ai_json(), feedback=None, previous_selections=None, serp=None):

    feedback_value = feedback() if callable(feedback) else feedback
    previous_selections_value = previous_selections() if callable(previous_selections) else previous_selections

    researcher_prompt = prompt.format(
        feedback=feedback_value,
        previous_selections=previous_selections_value,
        serp=serp().content,
        datetime=get_current_utc_datetime()
    )

    messages = [
        {"role": "system", "content": researcher_prompt},
        {"role": "human", "content": f"research question: {research_question}"}
    ]

    ai_msg = llm.invoke(messages)

    state = {**state, "researcher_response": ai_msg.content}

    return state

def reporter_agent(state:AgentGraphState, research_question, prompt=reporter_prompt_template, llm=get_open_ai(), feedback=None, previous_reports=None, research=None):

    feedback_value = feedback() if callable(feedback) else feedback
    previous_reports_value = previous_reports() if callable(previous_reports) else previous_reports
    research_value = research() if callable(research) else research
    
    
    reporter_prompt = prompt.format(
        feedback=feedback_value,
        previous_reports=previous_reports_value,
        datetime=get_current_utc_datetime(),
        research=research_value
    )

    messages = [
        {"role": "system", "content": reporter_prompt},
        {"role": "human", "content": f"research question: {research_question}"}
    ]

    ai_msg = llm.invoke(messages)
    
    print("\n\nREPORTER RESPONSE", ai_msg.content)

    state = {**state, "reporter_response": ai_msg.content}

    return state

def reviewer_agent(
        state:AgentGraphState,
        research_question,
        prompt=reviewer_prompt_template, 
        llm=get_open_ai_json(), 
        planner=None, 
        researcher=None, 
        reporter=None, 
        planner_agent=None, 
        researcher_agent=None, 
        reporter_agent=None,
          feedback=None):
    
    planner_value = planner() if callable(planner) else planner
    researcher_value = researcher() if callable(researcher) else researcher
    reporter_value = reporter() if callable(reporter) else reporter
    planner_agent_value = planner_agent
    researcher_agent_value = researcher_agent
    reporter_agent_value = reporter_agent
    # planner_agent_value = planner_agent() if callable(planner_agent) else planner_agent
    # researcher_agent_value = researcher_agent() if callable(researcher_agent) else researcher_agent
    # reporter_agent_value = reporter_agent() if callable(reporter_agent) else reporter_agent
    feedback_value = feedback() if callable(feedback) else feedback
    
    reviewer_prompt = prompt.format(
        planner = planner_value.content,
        researcher=researcher_value.content,
        reporter=reporter_value.content,
        planner_responsibilities=planner_agent_value,
        researcher_responsibilities=researcher_agent_value,
        reporter_responsibilities=reporter_agent_value,
        feedback=feedback_value,
        datetime=get_current_utc_datetime()
    )

    messages = [
        {"role": "system", "content": reviewer_prompt},
        {"role": "user", "content": f"research question: {research_question}"}
    ]

    ai_msg = llm.invoke(messages)

    print("REVIEWER RESPONSE", ai_msg.content)

    state = {**state, "reviewer_response": ai_msg.content}

    return state


def end_node(state:AgentGraphState):
    state = {**state, "end_chain": "End of the graph"}
    return state


    