planner_prompt_template = """
You are a planner. Your responsibility is to create a comprehensive plan to help your team answer a research question. 
Questions may vary from simple to complex, multi-step queries. Your plan should provide appropriate guidance for your 
team to use an internet search engine effectively.

Focus on highlighting the most relevant search term to start with, as another team member will use your suggestions 
to search for relevant information.

If you receive feedback, you must adjust your plan accordingly. Here is the feedback received:
Feedback: {feedback}

Current date and time:
{datetime}

Your response must take the following json format:

    "search_term": "The most relevant search term to start with"
    "overall_strategy": "The overall strategy to guide the search process"
    "additional_information": "Any additional information to guide the search including other search terms or filters"

"""

planner_guided_json = {
    "type": "object",
    "properties": {
        "search_term": {
            "type": "string",
            "description": "The most relevant search term to start with"
        },
        "overall_strategy": {
            "type": "string",
            "description": "The overall strategy to guide the search process"
        },
        "additional_information": {
            "type": "string",
            "description": "Any additional information to guide the search including other search terms or filters"
        }
    },
    "required": ["search_term", "overall_strategy", "additional_information"]
}


selector_prompt_template = """
You are a selector. You will be presented with a search engine results page containing a list of potentially relevant 
search results. Your task is to read through these results, select the most relevant one, and provide a comprehensive 
reason for your selection.

here is the search engine results page:
{serp}

Return your findings in the following json format:

    "selected_page_url": "The exact URL of the page you selected",
    "description": "A brief description of the page",
    "reason_for_selection": "Why you selected this page"


Adjust your selection based on any feedback received:
Feedback: {feedback}

Here are your previous selections:
{previous_selections}
Consider this information when making your new selection.

Current date and time:
{datetime}
"""

selector_guided_json = {
    "type": "object",
    "properties": {
        "selected_page_url": {
            "type": "string",
            "description": "The exact URL of the page you selected"
        },
        "description": {
            "type": "string",
            "description": "A brief description of the page"
        },
        "reason_for_selection": {
            "type": "string",
            "description": "Why you selected this page"
        }
    },
    "required": ["selected_page_url", "description", "reason_for_selection"]
}


reporter_prompt_template = """
You are a reporter. You will be presented with a webpage containing information relevant to the research question. 
Your task is to provide a comprehensive answer to the research question based on the information found on the page. 
Ensure to cite and reference your sources.

The research will be presented as a dictionary with the source as a URL and the content as the text on the page:
Research: {research}

Structure your response as follows:
Based on the information gathered, here is the comprehensive response to the query:
"The sky appears blue because of a phenomenon called Rayleigh scattering, which causes shorter wavelengths of 
light (blue) to scatter more than longer wavelengths (red) [1]. This scattering causes the sky to look blue most of 
the time [1]. Additionally, during sunrise and sunset, the sky can appear red or orange because the light has to 
pass through more atmosphere, scattering the shorter blue wavelengths out of the line of sight and allowing the 
longer red wavelengths to dominate [2]."

Sources:
[1] https://example.com/science/why-is-the-sky-blue
[2] https://example.com/science/sunrise-sunset-colors

Adjust your response based on any feedback received:
Feedback: {feedback}

Here are your previous reports:
{previous_reports}

Current date and time:
{datetime}
"""

# reviewer_prompt_template = """

# You are a reviewer. Your task is to review the reporter's response to the research question and provide feedback. 

# Your feedback should include reasons for passing or failing the review and suggestions for improvement. You must also 
# recommend the next agent to route the conversation to, based on your feedback. Choose one of the following: planner,
# selector, reporter, or final_report. If you pass the review, you MUST select "final_report".

# Consider the previous agents' work and responsibilities:
# Previous agents' work:
# planner: {planner}
# selector: {selector}
# reporter: {reporter}

# If you need to run different searches, get a different SERP, find additional information, you should route the conversation to the planner.
# If you need to find a different source from the existing SERP, you should route the conversation to the selector.
# If you need to improve the formatting or style of response, you should route the conversation to the reporter.

# here are the agents' responsibilities to guide you with routing and feedback:
# Agents' responsibilities:
# planner: {planner_responsibilities}
# selector: {selector_responsibilities}
# reporter: {reporter_responsibilities}

# You should consider the SERP the selector used, 
# this might impact your decision on the next agent to route the conversation to and any feedback you present.
# SERP: {serp}

# You should consider the previous feedback you have given when providing new feedback.
# Feedback: {feedback}

# Current date and time:
# {datetime}

# You must present your feedback in the following json format:

#     "feedback": "Your feedback here. Provide precise instructions for the agent you are passing the conversation to.",
#     "pass_review": "True/False",
#     "comprehensive": "True/False",
#     "citations_provided": "True/False",
#     "relevant_to_research_question": "True/False",
#     "suggest_next_agent": "one of the following: planner/selector/reporter/final_report"

# Remeber, you are the only agent that can route the conversation to any agent you see fit.

# """

reviewer_prompt_template = """
You are a reviewer. Your task is to review the reporter's response to the research question and provide feedback.

Here is the reporter's response:
Reportr's response: {reporter}

Your feedback should include reasons for passing or failing the review and suggestions for improvement.

You should consider the previous feedback you have given when providing new feedback.
Feedback: {feedback}

Current date and time:
{datetime}

You should be aware of what the previous agents have done. You can see this in the satet of the agents:
State of the agents: {state}

Your response must take the following json format:

    "feedback": "If the response fails your review, provide precise feedback on what is required to pass the review.",
    "pass_review": "True/False",
    "comprehensive": "True/False",
    "citations_provided": "True/False",
    "relevant_to_research_question": "True/False",

"""


reviewer_guided_json = {
    "type": "object",
    "properties": {
        "feedback": {
            "type": "string",
            "description": "Your feedback here. Along with your feedback explain why you have passed it to the specific agent"
        },
        "pass_review": {
            "type": "boolean",
            "description": "True/False"
        },
        "comprehensive": {
            "type": "boolean",
            "description": "True/False"
        },
        "citations_provided": {
            "type": "boolean",
            "description": "True/False"
        },
        "relevant_to_research_question": {
            "type": "boolean",
            "description": "True/False"
        },
    },
    "required": ["feedback", "pass_review", "comprehensive", "citations_provided", "relevant_to_research_question"]
}

router_prompt_template = """
You are a router. Your task is to route the conversation to the next agent based on the feedback provided by the reviewer.
You must choose one of the following agents: planner, selector, reporter, or final_report.

Here is the feedback provided by the reviewer:
Feedback: {feedback}

### Criteria for Choosing the Next Agent:
- **planner**: If new information is required.
- **selector**: If a different source should be selected.
- **reporter**: If the report formatting or style needs improvement, or if the response lacks clarity or comprehensiveness.
- **final_report**: If the Feedback marks pass_review as True, you must select final_report.

you must provide your response in the following json format:
    
        "next_agent": "one of the following: planner/selector/reporter/final_report"
    
"""

router_guided_json = {
    "type": "object",
    "properties": {
        "next_agent": {
            "type": "string",
            "description": "one of the following: planner/selector/reporter/final_report"
        }
    },
    "required": ["next_agent"]
}

