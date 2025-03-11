"""This "graph" is a hotel agent graph"""

from typing import TypedDict, Annotated
from langchain_aws import ChatBedrockConverse
import boto3
from langgraph.graph import StateGraph, START, MessagesState
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from hotel_agent.tools import (
    suggest_hotels,
    retrieve_hotel_booking,
    change_hotel_booking,
    cancel_hotel_booking,
)


bedrock_client = boto3.client("bedrock-runtime", region_name="us-west-2")

llm = ChatBedrockConverse(
    # model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    model="anthropic.claude-3-sonnet-20240229-v1:0",
    temperature=0,
    max_tokens=None,
    client=bedrock_client,
    # other params...
)

memory = MemorySaver()


class State(TypedDict):
    messages: Annotated[list, add_messages]
    next: str


primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant who manage hotel bookings. You have 'suggest_hotels' tool to suggest hotels",
        ),
        ("placeholder", "{messages}"),
    ]
)
hotel_tools = [
    suggest_hotels,
    retrieve_hotel_booking,
    change_hotel_booking,
    cancel_hotel_booking,
]

runnable_with_tools = primary_assistant_prompt | llm.bind_tools(hotel_tools)


def hotel_agent(state: State):
    return {"messages": [runnable_with_tools.invoke(state)]}


graph_builder = StateGraph(MessagesState, config_schema=RunnableConfig)
graph_builder.add_node("hotel_agent", hotel_agent)

tool_node = ToolNode(tools=hotel_tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "hotel_agent",
    tools_condition,
)
graph_builder.add_edge("tools", "hotel_agent")
graph_builder.add_edge(START, "hotel_agent")

graph = graph_builder.compile(checkpointer=memory)

graph.name = "HotelAgentGraph"
