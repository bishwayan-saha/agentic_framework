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
            return ""
        
@mcp.tool()
async def search_web_tool(query: str):

    """
        Search the web for information for a given query. The query can be related to any topic.
        With the help of Serper, you first fetch the relevant URLs.
        Then you fetch the content of the URLs and return the formatted text.

        Args:
            query: The query to search for basically a topic.
        Returns:
            The text from the all URL contents for the given query.
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