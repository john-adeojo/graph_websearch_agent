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

    planner_prompt = prompt.format(
        feedback=feedback,
        previous_plans=previous_plans,
        datetime=get_current_utc_datetime()
    )

    messages = [
        {"role": "system", "content": planner_prompt},
        {"role": "human", "content": f"research question: {research_question}"}
    ]

    # messages = [
    #     ("system", planner_prompt),
    #     ("human", f"research question:{research_question}. Respond in json.")
    # ]

    ai_msg = llm.invoke(messages)

    state = {**state, "planner_response": ai_msg.content}

    return state

def researcher_agent(state:AgentGraphState, research_question, prompt=researcher_prompt_template, llm=get_open_ai_json(), feedback=None, previous_selections=None, serp=None):

    researcher_prompt = prompt.format(
        feedback=feedback,
        previous_selections=previous_selections,
        serp=serp().content,
        datetime=get_current_utc_datetime()
    )

    messages = [
        {"role": "system", "content": researcher_prompt},
        {"role": "human", "content": f"research question: {research_question}"}
    ]

    # messages = [
    #     ("system", f"{researcher_prompt}"),
    #     ("human", f"research question:{research_question}. Respond in json.")
    # ]

    ai_msg = llm.invoke(messages)

    state = {**state, "researcher_response": ai_msg.content}

    return state

def reporter_agent(state:AgentGraphState, research_question, prompt=reporter_prompt_template, llm=get_open_ai(), feedback=None, previous_reports=None, research=None):

    reporter_prompt = prompt.format(
        feedback=feedback,
        previous_reports=previous_reports,
        datetime=get_current_utc_datetime(),
        research=research
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
    
    print("\n\n\n\nDENUGGING REVIEWER AGENT", f"planner: {planner()}, researcher: {researcher()}, reporter: {reporter()}, planner_agent: {planner_agent()}, researcher_agent: {researcher_agent()}, reporter_agent: {reporter_agent()}")

    reviewer_prompt = prompt.format(
        planner = planner,
        researcher=researcher,
        reporter=reporter,
        planner_responsibilities=planner_agent,
        researcher_responsibilities=researcher_agent,
        reporter_responsibilities=reporter_agent,
        feedback=feedback,
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


    