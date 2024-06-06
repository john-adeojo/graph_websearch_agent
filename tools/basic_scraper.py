import requests
from bs4 import BeautifulSoup

def is_garbled(text):
    # A simple heuristic to detect garbled text: high proportion of non-ASCII characters
    non_ascii_count = sum(1 for char in text if ord(char) > 127)
    return non_ascii_count > len(text) * 0.3

def scrape_website(research):

    url = research["selected_page_url"]

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
        
        return {"source": url, "content": content}
    
    except requests.RequestException as e:
        return {"source": url, "content": f"error in scraping website, {str(e)}"}
