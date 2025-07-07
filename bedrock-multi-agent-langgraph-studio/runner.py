from langchain_core.messages import HumanMessage
from src.supervisor_agent.graph import run_supervisor_agent
import sys
import boto3
import os
import json 


if __name__ == "__main__":
    user_prompt = sys.argv[1] if len(sys.argv) > 1 else "Default prompt here"
    message = HumanMessage(content=user_prompt)
    state = {"messages": [message]}
    result = run_supervisor_agent(state)
    # messages = result["messages"]
    # formatted = "\n---\n".join(
    #         f"🧠 {m.name or 'user'}:\n{m.content}" for m in messages
    #     )
    # print(formatted)
    # session_id = os.environ["SESSION_ID"]
    # s3_bucket = os.environ["S3_BUCKET"]
    # s3_key = f"results/{session_id}.json"
    # s3 = boto3.client("s3")
    # s3.put_object(
    #     Bucket=s3_bucket,
    #     Key=s3_key,
    #     Body=json.dumps(result),
    #     ContentType="application/json"
    # )
    print(result)
    