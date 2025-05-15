from pydantic import BaseModel, Field


class Message(BaseModel):
    query: str = Field(..., description="User query to host agent")
