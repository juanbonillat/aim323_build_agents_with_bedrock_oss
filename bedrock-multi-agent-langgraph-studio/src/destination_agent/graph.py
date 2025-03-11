"""This "graph" is a flight agent graph"""

from langchain_aws import ChatBedrockConverse
import boto3
from langgraph.graph import StateGraph, START, MessagesState
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from destination_agent.tools import compare_and_recommend_destination
from pydantic import BaseModel

bedrock_client = boto3.client("bedrock-runtime", region_name="us-west-2")

llm = ChatBedrockConverse(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    temperature=0,
    max_tokens=None,
    client=bedrock_client,
    # other params...
)
tools = [compare_and_recommend_destination]
llm_with_tools = llm.bind_tools(tools)

memory = MemorySaver()


class location(BaseModel):
    """
    Return departure city and destination city
    """

    current_location: str
    destination_city: str


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful assistant who can suggest destination location to the user. 
            You have access to 'compare_and_recommend_destination' tool that can search for the destination. 
            This tool already has information about user's current location.
        
        """,
        ),
        ("placeholder", "{messages}"),
    ]
)

destination_agent_chain = prompt | llm_with_tools


def destination_agent(state):
    result = destination_agent_chain.invoke(state)
    return {"messages": [result]}


graph_builder = StateGraph(MessagesState, config_schema=RunnableConfig)
graph_builder.add_node("destination_agent", destination_agent)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "destination_agent",
    tools_condition,
)
graph_builder.add_edge("tools", "destination_agent")
graph_builder.add_edge(START, "destination_agent")

graph = graph_builder.compile(checkpointer=memory)
graph.name = "PlannerGraph"
