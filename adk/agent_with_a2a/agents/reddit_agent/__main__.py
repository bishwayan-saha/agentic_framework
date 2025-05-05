# -----------------------------------------------------------------------------
## This is the main script which starts the RedditAgent server
## - Declares agent's capabilities
## - Sets up the A2A server with RedditAgent
## Starts listening on a specific host and port
# -----------------------------------------------------------------------------


from server.server import A2AServer
from models.agent import AgentCard, AgentCapabilities, AgentSkill
from agents.reddit_agent.task_manager import AgentTaskManager
from agents.reddit_agent.agent import RedditAgent
import click 

@click.command()
@click.option("--host", default="localhost", help="Host to bind the server to")
@click.option("--port", default=10002, help="Port number for the server")
def main(host, port):
    """
    This function sets up everything needed to start the agent server.
    You can run it via: `python -m agents.google_adk --host localhost(127.0.0.1) --port xxxxx`
    """

    # Define what this agent can do – in this case, it does NOT support streaming
    capabilities = AgentCapabilities(streaming=False)

    # Define the skill this agent offers (used in directories and UIs)
    skill = AgentSkill(
        id="fetch_reddit_post",
        name="Fetch Latest Reddit Posts Tool",
        description="Given a subreddit name, it fetch the latest posts of that subreddit and returns them in a formatted response",  # What the skill does
        tags=["reddit", "news", "posts", "subreddit"],
        examples=[
            "What are the latest posts on AI_Agents?",
            "Tell me the top news from gamedev",
        ],
    )

    # Create an agent card describing this agent's identity and metadata
    agent_card = AgentCard(
        name="RedditAgent",
        description="This agent replies fetched the latest posts from a given subreddit.",
        url=f"http://{host}:{port}/",
        version="1.0.0",
        defaultInputModes=RedditAgent.SUPPORTED_CONTENT_TYPES,
        defaultOutputModes=RedditAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=[skill],
    )

    server = A2AServer(
        host=host,
        port=port,
        agent_card=agent_card,
        task_manager=AgentTaskManager(agent=RedditAgent()),
    )

    server.start()


if __name__ == "__main__":
    main()
