# -----------------------------------------------------------------------------
## This is the main script which starts the RedditAgent server
## - Declares agent's capabilities
## - Sets up the A2A server with RedditAgent
## Starts listening on a specific host and port
# -----------------------------------------------------------------------------


import click
from agents.search_agent.agent import SearchAgent
from agents.search_agent.task_manager import SearchAgentTaskManager
from models.agent import AgentCapabilities, AgentCard, AgentSkill
from server.server import A2AServer


@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10001, help="Port number for the server")
def main(host, port):
    """
    This function sets up everything needed to start the agent server.
    """

    # Define what this agent can do – in this case, it does NOT support streaming
    capabilities = AgentCapabilities(streaming=False)

    # Define the skill this agent offers (used in directories and UIs)
    skill = AgentSkill(
        id="web_search_agent",
        name="Fetch information about a topic via google search",
        description="Given a query by user, search about in internet via google search and return a formatted response to the user",  # What the skill does
        tags=["search", "web"],
        examples=[
        ],
    )

    # Create an agent card describing this agent's identity and metadata
    agent_card = AgentCard(
        name="SearchAgent",
        description="This agent replies fetched relevant information from google web search.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=SearchAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=SearchAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill],
    )

    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=SearchAgentTaskManager(agent=SearchAgent()),
    )

    server.start()


if __name__ == "__main__":
    main()
