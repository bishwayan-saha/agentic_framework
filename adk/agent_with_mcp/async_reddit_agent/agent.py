from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from google.adk.agents import Agent
from dotenv import load_dotenv
import os

load_dotenv()

async def get_tools_async():
    print("--- Attempting to start and connect to mcp-reddit MCP server via uvx ---")
    tools, exit_stack = await MCPToolset.from_server(
        connection_params = StdioServerParameters(
            command="uvx",
            args=["--from", "git+https://github.com/adhikasp/mcp-reddit.git", "mcp-reddit"]
        )
    )

    print("--- Loaded tools ---")
    for tool in tools:
        print(f"--- Loaded tool: {tool.name} ---")

    return tools, exit_stack


async def create_async_reddit_agent():
    print("--- Creating agent ---")
    tools, exit_stack = await get_tools_async()

    agent = Agent(
        model="gemini-1.5-flash",
        name="async_reddit_agent",
        description="""
            A specialized Reddit agent that searches and returns for relevant posts on a given 
            subreddit using MCP Reddit server.
        """,
        instruction=(
            """You are the Async Reddit Agent. Your task is to fetch hot post titles from any subreddit using the connected Reddit MCP tool."
            "1. **Identify Subreddit:** Determine which subreddit the user wants news from. Use the specific subreddit mentioned (e.g., 'AI_Agents', 'agenticaidev')."
            "2. **Call Discovered Tool:** You **MUST** look for and call the available tools with the identified subreddit name and optionally a limit." # Adjust name if needed!
            "3. **Present Results:** The tool will return a formatted string containing the hot post information details or an error message."
            "   - Present this information details directly to the user."
            "   - Clearly state which subreddit the information is from."
            "   - If the tool returns an error message, relay that message accurately."
            "4. **Handle Missing Tool:** If you cannot find the required Reddit tool, inform the user that you cannot fetch Reddit news due to a configuration issue."
            "5. **Do Not Hallucinate:** Only provide information returned by the tool."""
        ),
        tools=tools
    )

    return agent, exit_stack

root_agent = create_async_reddit_agent()
    














