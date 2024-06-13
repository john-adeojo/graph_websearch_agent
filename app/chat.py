import os
import json
import yaml
import chainlit as cl
from chainlit.input_widget import TextInput, Slider, Select, NumberInput
from agent_graph.graph import create_graph, compile_workflow


def update_config(serper_api_key, openai_llm_api_key, groq_llm_api_key, claud_llm_api_key, gemini_llm_api_key):
    config_path = "G:/My Drive/Data-Centric Solutions/07. Digital Content/LangGraph/code/graph_websearch_agent/config/config.yaml"

    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    config['SERPER_API_KEY'] = serper_api_key
    config['OPENAI_API_KEY'] = openai_llm_api_key
    config['GROQ_API_KEY'] = groq_llm_api_key
    config['CLAUD_API_KEY'] = claud_llm_api_key
    config['GEMINI_API_KEY'] = gemini_llm_api_key

    if serper_api_key:
        os.environ['SERPER_API_KEY'] = serper_api_key
    if openai_llm_api_key:
        os.environ['OPENAI_API_KEY'] = openai_llm_api_key
    if groq_llm_api_key:
        os.environ['GROQ_API_KEY'] = groq_llm_api_key
    if claud_llm_api_key:
        os.environ['CLAUD_API_KEY'] = claud_llm_api_key
    if gemini_llm_api_key:
        os.environ['GEMINI_API_KEY'] = gemini_llm_api_key

    with open(config_path, 'w') as file:
        yaml.safe_dump(config, file)

    print("Configuration updated successfully.")

class ChatWorkflow:
    def __init__(self):
        self.workflow = None
        self.recursion_limit = 40

    def build_workflow(self, server, model, model_endpoint, temperature, recursion_limit=40, stop=None):
        graph = create_graph(
            server=server, 
            model=model, 
            model_endpoint=model_endpoint,
            temperature=temperature,
            stop=stop
        )
        self.workflow = compile_workflow(graph)
        self.recursion_limit = recursion_limit

    def invoke_workflow(self, message):
        if not self.workflow:
            return "Workflow has not been built yet. Please update settings first."
        
        dict_inputs = {"research_question": message.content}
        limit = {"recursion_limit": self.recursion_limit}
        reporter_state = None

        for event in self.workflow.stream(dict_inputs, limit):
            next_agent = ""
            if "router" in event.keys():
                state = event["router"]
                reviewer_state = state['router_response']
                # print("\n\nREVIEWER_STATE:", reviewer_state)
                reviewer_state_dict = json.loads(reviewer_state)
                next_agent_value = reviewer_state_dict["next_agent"]
                if isinstance(next_agent_value, list):
                    next_agent = next_agent_value[-1]
                else:
                    next_agent = next_agent_value

            if next_agent == "final_report":
                # print("\n\nEVENT_DEBUG:", event)
                state = event["router"]
                reporter_state = state['reporter_response']
                if isinstance(reporter_state, list):
                    print("LIST:", "TRUE")
                    reporter_state = reporter_state[-1]
                return reporter_state.content if reporter_state else "No report available"

        return "Workflow did not reach final report"

# Use a single instance of ChatWorkflow
chat_workflow = ChatWorkflow()

@cl.on_chat_start
async def start():
    await cl.ChatSettings(
        [
            Select(
                id="server",
                label="Select the server you want to use:",
                values=[
                    "openai",
                    "ollama",
                    "vllm",
                    "groq",
                    "claude",
                    "gemini"
                ]
            ),
            NumberInput(
                id="recursion_limit",
                label="Enter the recursion limit:",
                description="The maximum number of agent actions the workflow will take before stopping. The default value is 40",
                initial=40
            ),
            TextInput(
                id="google_serper_api_key",
                label="Enter your SERPER API Key:",
                description="You can get your API key from https://serper.dev/",
                # initial="NO_KEY_GIVEN"
                
            ),
            TextInput(
                id='openai_llm_api_key',
                label='Enter your OpenAI API Key:',
                description="Only use this if you are using an OpenAI Model.",
                # initial="NO_KEY_GIVEN"
            ),
            TextInput(
                id='groq_llm_api_key',
                label='Enter your Groq API Key:',
                description="Only use this if you are using Groq.",
                # initial="NO_KEY_GIVEN"
            ),
            TextInput(
                id='claud_llm_api_key',
                label='Enter your Claud API',
                description="Only use this if you are using Claud.",
            ),
            TextInput(
                id='gemini_llm_api_key',
                label='Enter your Gemini API',
                description="Only use this if you are using Gemini.",
            ),
            TextInput(
                id='llm_model',
                label='Enter your Model Name:',
                description="The name of the model you want to use"
            ),
            TextInput(
                id='server_endpoint',
                label='Your vLLM server endpoint:',
                description="Your HTTPs endpoint for the vLLM server. Only use if you are using a custom server"
            ),
            TextInput(
                id='stop_token',
                label='Stop token:',
                description="The token that will be used to stop the model from generating more text. The default value is <|end_of_text|>",
                initial="<|end_of_text|>"
            ),
            Slider(
                id='temperature',
                label='Temperature:',
                initial=0,
                max=1,
                step=0.05,
                description="Lower values will generate more deterministic responses, while higher values will generate more random responses. The default value is 0"
            )
        ]
    ).send()

@cl.on_settings_update
async def update_settings(settings):
    global author
    SERPER_API_KEY = settings["google_serper_api_key"]
    LLM_API_KEY = settings["openai_llm_api_key"]
    GROQ_API_KEY = settings["groq_llm_api_key"]
    CLAUD_API_KEY = settings["claud_llm_api_key"]
    GEMINI_API_KEY = settings["gemini_llm_api_key"]
    update_config(
        serper_api_key=SERPER_API_KEY, 
        openai_llm_api_key=LLM_API_KEY, 
        groq_llm_api_key=GROQ_API_KEY,
        claud_llm_api_key=CLAUD_API_KEY,
        gemini_llm_api_key=GEMINI_API_KEY
        )
    server = settings["server"]
    model = settings["llm_model"]
    model_endpoint = settings["server_endpoint"]
    temperature = settings["temperature"]
    recursion_limit = settings["recursion_limit"]
    stop = settings["stop_token"]
    author = settings["llm_model"]
    await cl.Message(content="✅ Settings updated successfully, building workflow...").send()
    chat_workflow.build_workflow(server, model, model_endpoint, temperature, recursion_limit, stop)
    await cl.Message(content="😊 Workflow built successfully.").send()

@cl.on_message
async def main(message: cl.Message):
    response = await cl.make_async(chat_workflow.invoke_workflow)(message)
    await cl.Message(content=f"{response}", author=author).send()