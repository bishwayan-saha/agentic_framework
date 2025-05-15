from fastapi import FastAPI, Depends

from models.task import Task
from client.client import A2AClient
from uuid import uuid4
from app.database.main import Database
from contextlib import asynccontextmanager
from app.models.request import Message
from sqlalchemy.ext.asyncio import AsyncSession


client = A2AClient(url="http://localhost:10000")

session_id = uuid4().hex

database =Database()

creds = {}

@asynccontextmanager
async def lifespan(api: FastAPI):
    
    creds = await database.get_all_credentials()
    print(creds)
    yield

app = FastAPI(lifespan=lifespan)

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

# @app.post("/register-agent")
# async def register_agent(agentServer: AgentServer):
#     url = agentServer.url
#     data = read_json()
#     data.append(url)
#     write_json(data)    
#     return "server addedd"