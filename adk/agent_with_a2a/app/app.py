from contextlib import asynccontextmanager
from typing import List
from uuid import uuid4

from app.database import SessionLocal
from app.models.db_models import (Credentials_Master,
                                  Remote_Agent_Details_Master)
from app.models.request import AgentDetails, Message
from app.service import save_agent_card
from client.client import A2AClient
from fastapi import Depends, FastAPI, status
from fastapi.responses import JSONResponse
from models.task import Task
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    db: Session = SessionLocal()
    try:
        credentials: List[Credentials_Master] = db.query(Credentials_Master).all() 
        app.state.credentials = {}
        for credential in credentials:
            app.state.credentials[credential.credential_name] = credential.credential_value

        remote_agents: List[Remote_Agent_Details_Master] = db.query(Remote_Agent_Details_Master).all()
        app.state.agent_cards = [agent.agent_details for agent in remote_agents]
        yield
    finally:
        db.close()  

app = FastAPI(lifespan=lifespan)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


client = A2AClient(url="http://localhost:10000")

    # Generate a new session ID if not provided (user passed 0)
session_id = uuid4().hex
@app.get("/credentials")
def get_credentials():
    return JSONResponse(content={"message": app.state.credentials})

@app.get("/agent_cards", status_code=status.HTTP_200_OK)
def get_agent_cards():
    return JSONResponse(content={"message": app.state.agent_cards})

@app.post("/response", status_code=status.HTTP_200_OK)
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

@app.post("/register_agent", status_code=status.HTTP_201_CREATED)
async def register_agent(agentDetails: AgentDetails, db: Session = Depends(get_db)):
    response = await save_agent_card(agentDetails=agentDetails, db=db)
    return JSONResponse(content=response)
    