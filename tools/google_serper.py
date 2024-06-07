import os
import ast
from langchain_community.utilities import GoogleSerperAPIWrapper
from utils.helper_functions import load_config
from states.state import AgentGraphState

config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')

def get_google_serper(state:AgentGraphState, plan=None):
    load_config(config_path)

    plan_data = plan().content
    plan_data = ast.literal_eval(plan_data)
    search = plan_data.get("search_term")

    print(f"search term: {search}")

    try:
        search = GoogleSerperAPIWrapper()
        results = search.results(search)
        state = {**state, "serper_response": results}
        return state
    except Exception as e:
        state = {**state, "serper_response": str(e)}
        return state


