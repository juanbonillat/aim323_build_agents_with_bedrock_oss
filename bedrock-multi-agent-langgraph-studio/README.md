# LangGraph Studio Multi-Agent System

This project demonstrates a multi-agent system built with LangGraph and Amazon Bedrock. The system consists of multiple specialized agents (destination, flight, hotel, and supervisor) that work together to provide travel recommendations and search for flights and hotels.

## Project Structure

```
langgraph-studio-multi-agent/
├── src/
│   ├── destination_agent/  # Agent for suggesting travel destinations
│   ├── flight_agent/       # Agent for searching and booking flights
│   ├── hotel_agent/        # Agent for searching and booking hotels
│   └── supervisor_agent/   # Orchestrator agent that coordinates the other agents
├── data/                   # Data files used by the agents
├── langgraph.json          # LangGraph configuration
└── pyproject.toml          # Project dependencies and configuration
```

## Prerequisites

- Python 3.11 or higher
- AWS account with access to Amazon Bedrock
- AWS CLI configured with appropriate credentials
- Access to Claude models in Amazon Bedrock

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd langgraph-studio-multi-agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the project and its dependencies:
   ```bash
   pip install -e .
   ```

## Amazon Bedrock Configuration

This project uses Amazon Bedrock for LLM capabilities. Here's how to set it up in your code:

1. **AWS Credentials**: Ensure your AWS credentials are properly configured either via environment variables, AWS CLI, or IAM roles.

2. **Bedrock Client Setup**: The project initializes a Bedrock client as follows:
   ```python
   import boto3
   
   bedrock_client = boto3.client("bedrock-runtime", region_name="us-west-2")
   ```

3. **LLM Configuration**: The project uses Claude models via the `ChatBedrockConverse` class:
   ```python
   from langchain_aws import ChatBedrockConverse
   
   llm = ChatBedrockConverse(
       model="anthropic.claude-3-5-sonnet-20240620-v1:0",  # or another Claude model
       temperature=0,
       max_tokens=None,
       client=bedrock_client,
   )
   ```

4. **Model Selection**: You can choose different Claude models based on your needs:
   - `anthropic.claude-3-5-sonnet-20240620-v1:0` (latest)
   - `anthropic.claude-3-sonnet-20240229-v1:0`
   - Other available Claude models in your Bedrock account

5. **Environment Variables**: Create a `.env` file in the project root with your AWS configuration if needed:
   ```
   AWS_REGION=us-west-2
   # Add other AWS configuration as needed
   ```

## Running LangGraph Studio

LangGraph Studio provides a visual interface to interact with and debug your agent graphs.

1. **Start LangGraph Studio**:
   ```bash
   langgraph studio
   ```

2. **Access the UI**: Open your browser and navigate to:
   ```
   https://smith.langchain.com/studio/thread?baseUrl=http://127.0.0.1:2024
   ```

3. **Interact with Agents**: You can interact with any of the defined agents:
   - Destination Agent: Suggests travel destinations
   - Flight Agent: Searches for flights
   - Hotel Agent: Searches for hotels
   - Supervisor Agent: Coordinates the other agents

4. **Testing the Multi-Agent System**: Try prompts like:
   ```
   Suggest me a travel destination and search flight and hotel for me. I want to travel on 15-March-2025 for 5 days
   ```

## Development

To add new agents or modify existing ones:

1. Create a new directory under `src/` for your agent
2. Implement the agent's graph in a `graph.py` file
3. Add any tools the agent needs
4. Register the agent in `langgraph.json`

## Troubleshooting

- **Bedrock Access Issues**: Ensure you have enabled the Claude models in your AWS Bedrock console
- **LangGraph Studio Connection Issues**: Check that all dependencies are installed correctly
- **Agent Errors**: Review the logs in LangGraph Studio for detailed error information

## Dependencies

This project relies on the following key libraries:
- `boto3`: AWS SDK for Python
- `langchain-aws`: LangChain integration with AWS services
- `langgraph`: Framework for building agent workflows
- `langgraph-cli`: CLI tools for LangGraph

For a complete list of dependencies, see `pyproject.toml`.
