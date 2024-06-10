
# Custom WebSearch Agent with LangGraph

### Watch the Tutorial:
[![Watch this video on YouTube](https://img.youtube.com/vi/R-o_a6dvzQM/0.jpg)](https://www.youtube.com/watch?v=R-o_a6dvzQM)


### Agent Schema:
![Agent Schema](schema_diagram/LanGraph.png)


### Prerequisites

#### Environment Setup
1. **Install Anaconda:**  
   Download Anaconda from [https://www.anaconda.com/](https://www.anaconda.com/).

2. **Create a Virtual Environment:**
   ```bash
   conda create -n agent_env python=3.11 pip
   ```
   
3. **Activate the Virtual Environment:**
   ```bash
   conda activate agent_env
   ```

### Clone and Navigate to the Repository
1. **Clone the Repo:**
   ```bash
   git clone https://github.com/john-adeojo/graph_websearch_agent.git
   ```

2. **Navigate to the Repo:**
   ```bash
   cd /path/to/your-repo/graph_websearch_agent
   ```

3. **Install Requirements:**
   ```bash
   pip install -r requirements.txt
   ```

### Configure API Keys
1. **Open the `config.yaml`:**
   ```bash
   nano config.yaml
   ```

2. **Enter API Keys:**
   - **Serper API Key:** Get it from [https://serper.dev/](https://serper.dev/)
   - **OpenAI API Key:** Get it from [https://openai.com/](https://openai.com/)

### Run Your Query
```bash
python -m app.app
```
Then enter your query.

## If you want to work with Ollama


### Setup Ollama Server
1. **Download Ollama:**
   Download [https://ollama.com/download](Ollama)

2. **Download an Ollama Model:**
   ```bash
   curl http://localhost:11434/api/pull -d "{\"name\": \"llama3\"}"
   ```
Ollama[https://github.com/ollama/ollama/blob/main/docs/api.md#list-local-models](API documentionation)

#### Video on how I integrated the Ollama Server:

[![Watch the video](https://img.youtube.com/vi/tVcOU054iWA/0.jpg)](https://youtu.be/tVcOU054iWA)
