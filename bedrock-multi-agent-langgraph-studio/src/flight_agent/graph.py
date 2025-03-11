"""This "graph" is a flight agent graph"""

from langchain_aws import ChatBedrockConverse
import boto3
from langgraph.graph import StateGraph, START, MessagesState
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from flight_agent.tools import (
    search_flights,
    retrieve_flight_booking,
    change_flight_booking,
    cancel_flight_booking,
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
tools = [
    search_flights,
    retrieve_flight_booking,
    change_flight_booking,
    cancel_flight_booking,
]
llm_with_tools = llm.bind_tools(tools)

memory = MemorySaver()

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a helpful agent who has tools to search flights. 
            'search_flights' tool already has information about user's current location
            """,
        ),
        ("placeholder", "{messages}"),
    ]
)

flight_agent_chain = prompt | llm_with_tools


def flight_agent(state):
    result = flight_agent_chain.invoke(state)
    return {"messages": [result]}


graph_builder = StateGraph(MessagesState, config_schema=RunnableConfig)
graph_builder.add_node("flight_agent", flight_agent)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "flight_agent",
    tools_condition,
)
graph_builder.add_edge("tools", "flight_agent")
graph_builder.add_edge(START, "flight_agent")

graph = graph_builder.compile(checkpointer=memory)
graph.name = "FlightAgentGraph"
