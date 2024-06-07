from langchain_openai import ChatOpenAI
from utils.helper_functions import load_config
import os

config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
load_config(config_path)

model = 'gpt-4o'

def get_open_ai(temperature=0):

    llm = ChatOpenAI(
    model=model,
    temperature = temperature,
)
    return llm

def get_open_ai_json(temperature=0):
    llm = ChatOpenAI(
    model=model,
    temperature = temperature,
    model_kwargs={"response_format": {"type": "json_object"}},
)
    return llm
