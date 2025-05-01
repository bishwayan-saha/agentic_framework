## This is the main script which starts the CurrentTimeAgent server
## - Declares agent's capabilities
## - Sets up the A2A server with CuurentTimeAgent 
## Starts listening on a specific host and port

from server.server import A2AServer

# Models for describing agent capabilities and metadata
from models.agent import AgentCard, AgentCapabilities, AgentSkill

# Task manager and agent logic
from agents.reddit_agent.task_manager import AgentTaskManager
from agents.reddit_agent.agent import RedditAgent
# CLI and logging support
import click           # For creating a clean command-line interface
import logging         # For logging errors and info to the console


# -----------------------------------------------------------------------------
# Setup logging to print info to the console
# -----------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Main Entry Function – Configurable via CLI
# -----------------------------------------------------------------------------

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10002, help="Port number for the server")
def main(host, port):
    """
    This function sets up everything needed to start the agent server.
    You can run it via: `python -m agents.google_adk --host 0.0.0.0 --port 12345`
    """

    # Define what this agent can do – in this case, it does NOT support streaming
    capabilities = AgentCapabilities(streaming=False)

    # Define the skill this agent offers (used in directories and UIs)
    skill = AgentSkill(
        id="fetch_reddit_post",                                 # Unique skill ID
        name="Fetch Latest Reddit Posts Tool",                          # Human-friendly name
        description="Given a subreddit name, it fetch the latest posts of that subreddit and returns them in a formatted response",    # What the skill does
        tags=["reddit", "news", "posts", "subreddit"],                                  # Optional tags for searching
        examples=["What are the latest posts on AI_Agents?", "Tell me the top news from gamedev"]  # Example queries
    )

    # Create an agent card describing this agent's identity and metadata
    agent_card = AgentCard(
        name="RedditAgent",                               # Name of the agent
        description="This agent replies fetched the latest posts from a given subreddit.",  # Description
        url=f"http://{host}:{port}/",                       # The public URL where this agent lives
        version="1.0.0",                                    # Version number
        defaultInputModes=RedditAgent.SUPPORTED_CONTENT_TYPES,  # Input types this agent supports
        defaultOutputModes=RedditAgent.SUPPORTED_CONTENT_TYPES, # Output types it produces
        capabilities=capabilities,                          # Supported features (e.g., streaming)
        skills=[skill]                                      # List of skills it supports
    )

    # Start the A2A server with:
    # - the given host/port
    # - this agent's metadata
    # - a task manager that runs the TellTimeAgent
    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=AgentTaskManager(agent=RedditAgent())
    )

    server.start()

if __name__ == "__main__":
    main()