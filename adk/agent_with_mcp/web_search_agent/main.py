import httpx
import json
import os
from bs4 import BeautifulSoup
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
load_dotenv()

SERPER_URL = "https://google.serper.dev/search"
mcp = FastMCP("web_search")

async def search_web(query: str) -> dict | None:
    payload = json.dumps({"q": query, "num": 3, "gl": "in"})
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(SERPER_URL, data=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)
            return None

async def fetch_url(url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            web_content = BeautifulSoup(response.text, "html.parser")
            text = web_content.get_text()
            return text
        except Exception as e:
            print(e)
            return None
        
@mcp.tool()
async def search_web_tool(query: str):

    """
        Search the web for documentation for a given query and library
        Supported libraries are langchain and llama-index.

        Args:
            query: The query to search for basically a topic
            library: The library in which to search
        Returns:
            The text from the documentation for the given query and library
    """

    search_res = await search_web(query)
    if not search_res["organic"]:
        raise ValueError("No results found")
    print("Results found")
    text = ""
    n = 0
    for url in search_res["organic"]:
        text += await fetch_url(url["link"])
    return text


def main():
    print("server started")
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()