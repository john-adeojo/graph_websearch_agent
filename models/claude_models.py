import requests
import json
import os
from utils.helper_functions import load_config
from langchain_core.messages.human import HumanMessage

class ClaudJSONModel:
    def __init__(self, temperature=0, model=None):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
        load_config(config_path)
        self.api_key = os.environ.get("CLAUD_API_KEY")
        self.headers = {
            'Content-Type': 'application/json', 
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
        self.model_endpoint = "https://api.anthropic.com/v1/messages"
        self.temperature = temperature
        self.model = model

    def invoke(self, messages):
        system = messages[0]["content"]
        user = messages[1]["content"]

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": f"system:{system}. Your output must be json formatted. Just return the specified json format, do not prepend your response with anything. \n\n user:{user}"
                }
            ],
            "max_tokens": 1024,
            "temperature": self.temperature,
        }

        try:
            request_response = requests.post(
                self.model_endpoint, 
                headers=self.headers, 
                data=json.dumps(payload)
            )
            
            print("\n\nREQUEST RESPONSE", request_response.status_code)
            # print("\n\nREQUEST RESPONSE HEADERS", request_response.headers)
            # print("\n\nREQUEST RESPONSE TEXT", request_response.text)
            
            request_response_json = request_response.json()
            # print("REQUEST RESPONSE JSON", request_response_json)

            if 'content' not in request_response_json or not request_response_json['content']:
                raise ValueError("No content in response")

            response_content = request_response_json['content'][0]['text']
            # print("RESPONSE CONTENT", response_content)
            
            response = json.loads(response_content)
            response = json.dumps(response)

            response_formatted = HumanMessage(content=response)

            return response_formatted
        except (requests.RequestException, ValueError, KeyError, json.JSONDecodeError) as e:
            error_message = f"Error in invoking model! {str(e)}"
            print("ERROR", error_message)
            response = {"error": error_message}
            response_formatted = HumanMessage(content=json.dumps(response))
            return response_formatted

class ClaudModel:
    def __init__(self, temperature=0, model=None):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
        load_config(config_path)
        self.api_key = os.environ.get("CLAUD_API_KEY")
        self.headers = {
            'Content-Type': 'application/json', 
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
        self.model_endpoint = "https://api.anthropic.com/v1/messages"
        self.temperature = temperature
        self.model = model

    def invoke(self, messages):
        system = messages[0]["content"]
        user = messages[1]["content"]

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": f"system:{system}\n\n user:{user}"
                }
            ],
            "max_tokens": 1024,
            "temperature": self.temperature,
        }

        try:
            request_response = requests.post(
                self.model_endpoint, 
                headers=self.headers, 
                data=json.dumps(payload)
            )
            
            print("REQUEST RESPONSE", request_response.status_code)
            # print("REQUEST RESPONSE HEADERS", request_response.headers)
            # print("REQUEST RESPONSE TEXT", request_response.text)
            
            request_response_json = request_response.json()
            # print("REQUEST RESPONSE JSON", request_response_json)

            if 'content' not in request_response_json or not request_response_json['content']:
                raise ValueError("No content in response")

            response_content = request_response_json['content'][0]['text']
            response_formatted = HumanMessage(content=response_content)

            return response_formatted
        except (requests.RequestException, ValueError, KeyError, json.JSONDecodeError) as e:
            error_message = f"Error in invoking model! {str(e)}"
            print("ERROR", error_message)
            response = {"error": error_message}
            response_formatted = HumanMessage(content=json.dumps(response))
            return response_formatted
