from langchain_groq import ChatGroq
from utils.helper_functions import load_config
import os

config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
load_config(config_path)

def get_groq(temperature=0, model='llama3-70b-8192'):
    
    chat = ChatGroq(
        temperature=temperature, 
        model_name=model
)
    return chat

def get_groq_json(temperature=0, model='llama3-70b-8192'):
    
    chat = ChatGroq(
        temperature=temperature, 
        model_name=model,
        model_kwargs={"response_format": {"type": "json_object"}},
)
    return chat