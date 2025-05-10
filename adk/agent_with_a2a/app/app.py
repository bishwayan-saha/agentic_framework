from fastapi import FastAPI
from pydantic import BaseModel, Field
from models.task import Task
from client.client import A2AClient
from uuid import uuid4
from app.service import read_json, write_json
app = FastAPI()

class Message(BaseModel):
    query: str = Field(..., description="User query to host agent")

class AgentServer(BaseModel):
    url: str = Field(..., description="URL of agent server")

client = A2AClient(url="http://localhost:10000")

    # Generate a new session ID if not provided (user passed 0)
session_id = uuid4().hex

@app.post("/")
async def get_response(message: Message):
    payload = {
            "id": uuid4().hex,
            "sessionId": session_id,
            "message": {
                "role": "user",  
                "parts": [
                    {"type": "text", "text": message.query}
                ]
            },
        }
    try:
        task: Task = await client.send_task(payload)
        if task.history and len(task.history) > 1:
            reply = task.history[-1]
            return reply.parts[0].text
        else:
            return "No response"
    except Exception as e:
        print("No No")

@app.post("/register-agent")
async def register_agent(agentServer: AgentServer):
    url = agentServer.url
    data = read_json()
    data.append(url)
    write_json(data)    
    return "server addedd"