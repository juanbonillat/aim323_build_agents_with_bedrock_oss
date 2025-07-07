# app.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from src.supervisor_agent.graph import run_supervisor_agent

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or restrict to Windmill's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_endpoint(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    result = run_supervisor_agent({"messages": messages})
    return result
