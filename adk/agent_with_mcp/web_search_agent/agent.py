from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from dotenv import load_dotenv
import os
from google.adk.agents import Agent
load_dotenv()

async def get_tools_async():
    tools, exit_stack = await MCPToolset.from_server(
        connection_params = StdioServerParameters(
            command="uv",
            args=[
                "--directory", 
                  "/home/bishwayansaha99/Python_Projects/adk/agent_with_mcp/web_search_agent",
                   "run",
                 "main.py"]
        )
    )

    print("--- Loaded tools ---")
    for tool in tools:
        print(f"--- Loaded tool: {tool.name} ---")

    return tools, exit_stack

async def create_web_search_agent():
    print("--- Creating agent ---")
    tools, exit_stack = await get_tools_async()

    agent = Agent(
        model="gemini-2.0-flash",
        name="web_search_agent",
        description="""
            A specialized web search agent that searches the web for information on a given topic.
        """,
        instruction=("""
            You are the Web Search Agent. Your task is to search the web for information on a given topic.
            1. **Identify Topic:** Determine the specific topic or question the user wants information on.
            2. **Call Discovered Tool:** You **MUST** look for and call the available tools with the identified topic.
            3. **Present Results:** The tool will return a raw text string containing the web search results. 
                     You will format the text in hearders, paragraphs, bullet points and add some emojis. 
                     *You will also add a disclaimer that the information is not verified and should be used with caution.*
            4. **Handle Missing Tool:** If you cannot find the required web search tool, inform the user that you cannot search the web due to a configuration issue.
            5. **Do Not Hallucinate:** Only provide information returned by the tool.
        """
            
        ),
        tools=tools
    )

    return agent, exit_stack

root_agent = create_web_search_agent()