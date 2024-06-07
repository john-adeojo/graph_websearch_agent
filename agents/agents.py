import yaml
import os
from termcolor import colored
from models.openai_models import get_open_ai, get_open_ai_json
from prompts.prompts import (
    planner_prompt_template,
    researcher_prompt_template,
    reporter_prompt_template,
    reviewer_prompt_template
)
from utils.helper_functions import get_current_utc_datetime, check_for_content
from states.state import AgentGraphState



def planner_agent(state:AgentGraphState, research_question, prompt=planner_prompt_template, llm=get_open_ai_json(), feedback=None, previous_plans=None):

    feedback_value = feedback() if callable(feedback) else feedback
    previous_plans_value = previous_plans() if callable(previous_plans) else previous_plans

    feedback_value = check_for_content(feedback_value)
    previous_plans_value = check_for_content(previous_plans_value)

    planner_prompt = prompt.format(
        feedback=feedback_value,
        previous_plans=previous_plans_value,
        datetime=get_current_utc_datetime()
    )


    messages = [
        {"role": "system", "content": planner_prompt},
        {"role": "user", "content": f"research question: {research_question}"}
    ]

    ai_msg = llm.invoke(messages)

    state = {**state, "planner_response": ai_msg.content}

    print(colored(f"Planner 👩🏿‍💻: {ai_msg.content}", 'cyan'))

    # print("Planner:", ai_msg.content)

    return state

def researcher_agent(state:AgentGraphState, research_question, prompt=researcher_prompt_template, llm=get_open_ai_json(), feedback=None, previous_selections=None, serp=None):

    feedback_value = feedback() if callable(feedback) else feedback
    previous_selections_value = previous_selections() if callable(previous_selections) else previous_selections

    feedback_value = check_for_content(feedback_value)
    previous_selections_value = check_for_content(previous_selections_value)

    researcher_prompt = prompt.format(
        feedback=feedback_value,
        previous_selections=previous_selections_value,
        serp=serp().content,
        datetime=get_current_utc_datetime()
    )

    messages = [
        {"role": "system", "content": researcher_prompt},
        {"role": "user", "content": f"research question: {research_question}"}
    ]

    ai_msg = llm.invoke(messages)

    print(colored(f"Researcher 🧑🏼‍💻: {ai_msg.content}", 'green'))

    state = {**state, "researcher_response": ai_msg.content}

    return state

def reporter_agent(state:AgentGraphState, research_question, prompt=reporter_prompt_template, llm=get_open_ai(), feedback=None, previous_reports=None, research=None):

    feedback_value = feedback() if callable(feedback) else feedback
    previous_reports_value = previous_reports() if callable(previous_reports) else previous_reports
    research_value = research() if callable(research) else research

    feedback_value = check_for_content(feedback_value)
    previous_reports_value = check_for_content(previous_reports_value)
    research_value = check_for_content(research_value)
    
    reporter_prompt = prompt.format(
        feedback=feedback_value,
        previous_reports=previous_reports_value,
        datetime=get_current_utc_datetime(),
        research=research_value
    )

    messages = [
        {"role": "system", "content": reporter_prompt},
        {"role": "user", "content": f"research question: {research_question}"}
    ]

    ai_msg = llm.invoke(messages)
    
    print(colored(f"Reporter 👨‍💻: {ai_msg.content}", 'yellow'))
    # print("Reporter (Draft):", ai_msg.content)

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
        feedback=None,
        serp=None
        ):
    
    planner_value = planner() if callable(planner) else planner
    researcher_value = researcher() if callable(researcher) else researcher
    reporter_value = reporter() if callable(reporter) else reporter
    planner_agent_value = planner_agent
    researcher_agent_value = researcher_agent
    reporter_agent_value = reporter_agent
    feedback_value = feedback() if callable(feedback) else feedback

    planner_value = check_for_content(planner_value)
    researcher_value = check_for_content(researcher_value)
    reporter_value = check_for_content(reporter_value)
    feedback_value = check_for_content(feedback_value)
    
    reviewer_prompt = prompt.format(
        planner = planner_value,
        researcher=researcher_value,
        reporter=reporter_value,
        planner_responsibilities=planner_agent_value,
        researcher_responsibilities=researcher_agent_value,
        reporter_responsibilities=reporter_agent_value,
        feedback=feedback_value,
        datetime=get_current_utc_datetime(),
        serp=serp().content
    )

    messages = [
        {"role": "system", "content": reviewer_prompt},
        {"role": "user", "content": f"research question: {research_question}"}
    ]

    ai_msg = llm.invoke(messages)

    print(colored(f"Reviewer 👩🏽‍⚖️: {ai_msg.content}", 'magenta'))
    # print("Reviewer Assessment", ai_msg.content)
    # custom_print(f"Reviewer Assessment: {ai_msg.content}")

    state = {**state, "reviewer_response": ai_msg.content}

    return state


def final_report(state:AgentGraphState, final_response=None):
    final_response_value = final_response() if callable(final_response) else final_response


    print(colored(f"Final Report 📝: {final_response_value.content}", 'blue'))
    # print("Final Report:", final_response_value.content)
    # custom_print(f"Final Report: {final_response_value.content}")

    state = {**state, "final_reports": final_response_value.content}

    return state

def end_node(state:AgentGraphState):
    state = {**state, "end_chain": "end_chain"}
    return state


    