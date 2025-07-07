from typing import TypedDict, Literal, Annotated
from pydantic import BaseModel
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage
from langchain_aws import ChatBedrockConverse
import boto3
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
from langgraph.graph import END, StateGraph, START
import functools
from flight_agent import graph as flight_agent_graph
from hotel_agent import graph as hotel_agent_graph
from destination_agent import graph as destination_agent_graph
from os import environ


members = ["flight_agent", "hotel_agent", "destination_agent"]
options = ["FINISH"] + members
#memory = MemorySaver()

bedrock_client = boto3.client("bedrock-runtime", region_name="us-east-1")

llm = ChatBedrockConverse(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",
    temperature=0,
    max_tokens=None,
    client=bedrock_client,
    # other params...
)


class routeResponse(BaseModel):
    """
    Return next agent name.
    """

    next: Literal[*options]


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
        Given the conversation below who should act next
        1. Suggest vacation destination using 'destination_agent'. Get the current location and recommended destination  from 'destination_agent' then to call 'flight_agent'
        2. Don't ask user for any confirmation. Just give flight and hotel options
        3. Use 'flight_agent' to search flights. Send destination city and travel date to flight agent
        4. Once 'flight_agent' has finished call 'hotel_agent' to search hotels. Do not ask user to book flights.
        5. If you have the answer return 'FINISH'
        6. When member has finished the task, and you notice FINISHED in the message then don't repeat same member again
        
        """,
        ),
        ("placeholder", "{messages}"),
    ]
).partial(options=str(options), members=", ".join(members))

supervisor_chain = prompt | llm.with_structured_output(routeResponse)


class State(TypedDict):
    messages: Annotated[list, add_messages]
    next: str | None


def supervisor_agent(state: State):
    result = supervisor_chain.invoke(state)
    output = {
        "next": result.next,
        "messages": [
            HumanMessage(
                content=f"Supervisor decided: {result.next}", name="supervisor"
            )
        ],
    }
    print(f"Supervisor output: {output}")
    return output

import pprint

def agent_node(state, agent, name):
    result = agent.invoke(state)
    pprint.pprint(result["messages"][-1].dict())

    #print(result["messages"][-1].content[0]["text"])
    return {
        "messages": [
            #HumanMessage(content=result["messages"][-1].content[0]["text"], name=name)
            HumanMessage(content=result["messages"][-1].content, name=name)
        ]
    }

# def agent_node(state, agent, name):
#     result = agent.invoke(state)

#     # Get last message (should be AIMessage)
#     last_msg = result["messages"][-1]
#     content = last_msg.content

#     # Make sure we're appending to history
#     updated_messages = state["messages"] + [
#         HumanMessage(content=content, name=name)
#     ]

#     return {
#         "messages": updated_messages,
#         "next": None
#     }



full_workflow = StateGraph(State, config_schema=RunnableConfig)
full_workflow.add_node("supervisor", supervisor_agent)

full_workflow.add_edge(START, "supervisor")

planner_node = functools.partial(
    agent_node, agent=destination_agent_graph, name="destination_agent"
)

flight_node = functools.partial(
    agent_node, agent=flight_agent_graph, name="flight_agent"
)

hotel_node = functools.partial(agent_node, agent=hotel_agent_graph, name="hotel_agent")

full_workflow.add_node("destination_agent", planner_node)
full_workflow.add_node("flight_agent", flight_node)
full_workflow.add_node("hotel_agent", hotel_node)


def process_output(state):
    messages = state["messages"]
    for message in reversed(messages):
        if isinstance(message, AIMessage) and isinstance(message.content, str):
            print(message.content)
            return {
                "messages": [HumanMessage(content=message.content, name="hotel_agent")]
            }
    return None


# full_workflow.add_node("process_output", process_output)
full_workflow.add_edge("destination_agent", "supervisor")
full_workflow.add_edge("flight_agent", "supervisor")
full_workflow.add_edge("hotel_agent", "supervisor")
# full_workflow.add_edge("process_output", "supervisor")

conditional_map = {k: k for k in members}
conditional_map["FINISH"] = END
full_workflow.add_conditional_edges("supervisor", lambda x: x["next"], conditional_map)

#graph = full_workflow.compile(
#    checkpointer=memory,
#)

if environ.get("env","") == "":
    memory = MemorySaver()
    graph = full_workflow.compile(checkpointer=memory)
else:
    graph = full_workflow.compile()

graph.name = "SupervisorAgentGraph"

def run_supervisor_agent(input):
    """Wrap graph invocation for Windmill"""
    config = RunnableConfig(configurable={"thread_id": "local-test","configurable":{"user_id":918}})
    result = graph.invoke(input,config=config)
    return result
