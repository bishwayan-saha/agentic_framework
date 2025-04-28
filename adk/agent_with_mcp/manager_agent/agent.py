from google.adk.agents import Agent
from async_reddit_agent.agent import create_async_reddit_agent
from summarizer_agent.agent import create_summarizer_agent 
from dotenv import load_dotenv
from contextlib import AsyncExitStack
load_dotenv()

async def create_manager_agent():
    """--- Creates the manager agent ---"""
    exit_stack = AsyncExitStack()
    await exit_stack.__aenter__()
    async_reddit_agent, reddit_exit_stack = await create_async_reddit_agent()
    summarizer_agent = create_summarizer_agent()

    agent = Agent(
        model = "gemini-1.5-flash",
        name = "manager_agent",
        description = "A helpful assistant that manages the available agents.",
        instruction = """
                        You are a helpful assistant that manages the Reddit agent and the summarizer agent.
                        You will procss the user query first.
                        - If its related to Reddit posts, you will pass it to the *async_reddit_agent*.
                        - If its related to summarizing, you will pass it to the *summarizer agent*.
                        - If its unrelated, you will use your intelligence to provide a general answer 
                          without any tool delegation.
                    """,
        sub_agents = [async_reddit_agent, summarizer_agent]
    )
    return agent, exit_stack

root_agent = create_manager_agent()

