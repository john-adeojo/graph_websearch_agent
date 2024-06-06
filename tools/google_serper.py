import os
from langchain_community.utilities import GoogleSerperAPIWrapper
from utils.helper_functions import load_config

config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')

def get_google_serper(plan):
    load_config(config_path)
    try:
        search = plan["search_term"]
        search = GoogleSerperAPIWrapper()
        results = search.get_search_results(search)
        return results
    except Exception as e:
        return {"error getting SERP": str(e)}


