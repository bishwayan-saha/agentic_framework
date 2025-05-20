import httpx, json
from app.models.db_models import Remote_Agent_Details_Master
from app.models.request import AgentDetails
from sqlalchemy.orm import Session


async def save_agent_card(agentDetails: AgentDetails, db: Session):
    async with httpx.AsyncClient() as client:
        well_known_url = f"{agentDetails.url.rstrip("/")}/.well-known/agent.json"
        response = await client.get(well_known_url)
        response.raise_for_status()

        remote_agent_details = Remote_Agent_Details_Master(
            agent_name=agentDetails.agent_name,
            server_url=agentDetails.url,
            agent_details=str(response.json()),
            created_by="bishwayan.saha@pwc.com",
        )
        try:
            db.add(remote_agent_details)
            db.commit()
            db.refresh(remote_agent_details)
            return {
                "message": "Agent added successfully!",
                "agent_id": str(remote_agent_details.agent_id),
                "agent_name": remote_agent_details.agent_name,
                "server_url": remote_agent_details.server_url,
                "agent_card": response.json(),
            }
        except Exception as e:
            db.rollback()
            return {"error": f"Failed to add agent, reason: {str(e)}"}
