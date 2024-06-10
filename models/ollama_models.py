import requests
import json
import ast
from langchain_core.messages.human import HumanMessage

class OllamaJSONModel:
    def __init__(self, temperature=0, model="llama3:instruct"):
        self.headers = {"Content-Type": "application/json"}
        self.model_endpoint = "http://localhost:11434/api/generate"
        self.temperature = temperature
        self.model = model

    def invoke(self, messages):

        system = messages[0]["content"]
        user = messages[1]["content"]

        payload = {
                "model": self.model,
                "prompt": user,
                "format": "json",
                "system": system,
                "stream": False,
                "temperature": 0,
            }
        
        try:
            request_response = requests.post(
                self.model_endpoint, 
                headers=self.headers, 
                data=json.dumps(payload)
                )
            
            print("REQUEST RESPONSE", request_response)
            request_response_json = request_response.json()
            # print("REQUEST RESPONSE JSON", request_response_json)
            response = json.loads(request_response_json['response'])
            response = json.dumps(response)

            response_formatted = HumanMessage(content=response)

            return response_formatted
        except requests.RequestException as e:
            response = {"error": f"Error in invoking model! {str(e)}"}
            response_formatted = HumanMessage(content=response)
            return response_formatted

class OllamaModel:
    def __init__(self, temperature=0, model="llama3:instruct"):
        self.headers = {"Content-Type": "application/json"}
        self.model_endpoint = "http://localhost:11434/api/generate"
        self.temperature = temperature
        self.model = model

    def invoke(self, messages):

        system = messages[0]["content"]
        user = messages[1]["content"]

        payload = {
                "model": self.model,
                "prompt": user,
                "system": system,
                "stream": False,
                "temperature": 0,
            }
        
        try:
            request_response = requests.post(
                self.model_endpoint, 
                headers=self.headers, 
                data=json.dumps(payload)
                )
            
            print("REQUEST RESPONSE JSON", request_response)

            request_response_json = request_response.json()['response']
            response = str(request_response_json)
            
            response_formatted = HumanMessage(content=response)

            return response_formatted
        except requests.RequestException as e:
            response = {"error": f"Error in invoking model! {str(e)}"}
            response_formatted = HumanMessage(content=response)
            return response_formatted

