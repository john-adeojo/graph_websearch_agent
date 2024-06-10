import json 
import requests
import ast
from bs4 import BeautifulSoup
from states.state import AgentGraphState
from langchain_core.messages import HumanMessage

def is_garbled(text):
    # A simple heuristic to detect garbled text: high proportion of non-ASCII characters
    non_ascii_count = sum(1 for char in text if ord(char) > 127)
    return non_ascii_count > len(text) * 0.3

def scrape_website(state: AgentGraphState, research=None):
    research_data = research().content
    research_data = json.loads(research_data)
    # research_data = ast.literal_eval(research_data)

    try:
        url = research_data["selected_page_url"]
    except KeyError as e:
        url = research_data["error"]

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract text content
        texts = soup.stripped_strings
        content = ' '.join(texts)
        
        # Check for garbled text
        if is_garbled(content):
            content = "error in scraping website, garbled text returned"
        else:
            # Limit the content to 4000 characters
            content = content[:4000]

        state["scraper_response"].append(HumanMessage(role="system", content=str({"source": url, "content": content})))
        
        return {"scraper_response": state["scraper_response"]}
    
    except requests.HTTPError as e:
        if e.response.status_code == 403:
            content = f"error in scraping website, 403 Forbidden for url: {url}"
        else:
            content = f"error in scraping website, {str(e)}"
        
        state["scraper_response"].append(HumanMessage(role="system", content=str({"source": url, "content": content})))
        return {"scraper_response": state["scraper_response"]}
    except requests.RequestException as e:
        content = f"error in scraping website, {str(e)}"
        state["scraper_response"].append(HumanMessage(role="system", content=str({"source": url, "content": content})))
        return {"scraper_response": state["scraper_response"]}

# import requests
# import ast
# from bs4 import BeautifulSoup
# from states.state import AgentGraphState
# from langchain_core.messages import HumanMessage
# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry

# def is_garbled(text):
#     # A simple heuristic to detect garbled text: high proportion of non-ASCII characters
#     non_ascii_count = sum(1 for char in text if ord(char) > 127)
#     return non_ascii_count > len(text) * 0.3

# def get_session_with_retries():
#     session = requests.Session()
#     retry = Retry(
#         total=5,  # Total number of retries
#         read=5,  # Number of retries on read errors
#         connect=5,  # Number of retries on connection errors
#         backoff_factor=0.3,  # Factor by which the delay between retries increases
#         status_forcelist=(500, 502, 504)  # Retry on these HTTP status codes
#     )
#     adapter = HTTPAdapter(max_retries=retry)
#     session.mount('http://', adapter)
#     session.mount('https://', adapter)
#     return session

# def scrape_website(state: AgentGraphState, research=None):
#     research_data = research().content
#     research_data = ast.literal_eval(research_data)
#     url = research_data["selected_page_url"]
    
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
#     }

#     try:
#         session = get_session_with_retries()
#         response = session.get(url, headers=headers)
#         response.raise_for_status()
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # Extract text content
#         texts = soup.stripped_strings
#         content = ' '.join(texts)
        
#         # Check for garbled text
#         if is_garbled(content):
#             content = "error in scraping website, garbled text returned"
#         else:
#             # Limit the content to 4000 characters
#             content = content[:4000]

#         state["scraper_response"].append(HumanMessage(role="system", content=str({"source": url, "content": content})))
        
#         return {"scraper_response": state["scraper_response"]}
    
#     except requests.HTTPError as e:
#         if e.response.status_code == 403:
#             content = f"error in scraping website, 403 Forbidden for url: {url}"
#         else:
#             content = f"error in scraping website, {str(e)}"
        
#         state["scraper_response"].append(HumanMessage(role="system", content=str({"source": url, "content": content})))
#         return {"scraper_response": state["scraper_response"]}
#     except requests.RequestException as e:
#         content = f"error in scraping website, {str(e)}"
#         state["scraper_response"].append(HumanMessage(role="system", content=str({"source": url, "content": content})))
#         return {"scraper_response": state["scraper_response"]}
