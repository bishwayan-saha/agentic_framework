from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text
Base = declarative_base()

class Remote_Agent_Master(Base):
    __tablename__ = "REMOTE_AGENT_MASTER"
    agent_id = Column(name="AGENT_ID", type_=Integer, primary_key=True, index=True)
    server_url = Column(name="SERVER_URL", type_=String, nullable=False)
    agent_name = Column(name="AGENT_NAME", type_=String)
    agent_card = Column(name="AGENT_CARD", type_=Text)

   



class Credentials_Master(Base):
    __tablename__ = "CREDENTIALS_MASTER"
    credential_name = Column(name="credential_name", type_=String, primary_key=True, index=True)
    credential_value = Column(name="credential_value", type_=Text, nullable=False)

    def __str__(self):
        return f"{self.credential_name} -> {self.credential_value}"