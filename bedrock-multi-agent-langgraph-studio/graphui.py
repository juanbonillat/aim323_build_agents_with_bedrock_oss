import gradio as gr
from langchain_core.messages import HumanMessage
from src.supervisor_agent.graph import run_supervisor_agent  # assumes this is defined

# def chat(user_input, history):
#     message = {"role": "user", "content": user_input}
#     messages = history + [message]
#     input_state = {"messages": [HumanMessage(**m) for m in messages]}
    
#     result = run_supervisor_agent(input_state)
    
#     # get the last AI message content from the result
#     final_msg = result["messages"][-1]
#     return history + [message, {"role": "assistant", "content": final_msg.content}]

def chat(user_input, history):
    # Add user's message to the state
    message = {"role": "user", "content": user_input}
    messages = history + [message]
    input_state = {"messages": [HumanMessage(**m) for m in messages]}

    result = run_supervisor_agent(input_state)

    # Append user message
    updated_history = history + [message]

    # Append ALL assistant (AI/supervisor) messages
    for msg in result["messages"]:
        if hasattr(msg, "content") and isinstance(msg.content, str):
            updated_history.append({"role": "assistant", "content": msg.content})

    return updated_history

gr.ChatInterface(
    fn=chat,
    chatbot=gr.Chatbot(label="Supervisor Agent"),
    title="Travel Planner",
    type="messages",
).launch(server_name="0.0.0.0", server_port=7860)
