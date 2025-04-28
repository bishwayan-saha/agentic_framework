from google.adk.agents import Agent
import os
import praw

def get_reddit_news(subreddit: str, limit:int = 3) -> dict[str, list[str]]:
    """
    Fetches top post titles from a specified subreddit using the Reddit API.

    Args:
        subreddit: The name of the subreddit to fetch news from.
        limit: The maximum number of top posts to fetch.

    Returns:
        A dictionary with the subreddit name as key and a list of
        post titles as value. Returns an error message if credentials are
        missing, the subreddit is invalid, or an API error occurs.
    """

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    try:
        reddit = praw.Reddit(client_id=client_id, client_secret=client_secret, user_agent=user_agent)
        sub_reddit = reddit.subreddit(subreddit)
        posts = list(sub_reddit.hot(limit=limit))
        titles = [post.title for post in posts]
        return {subreddit: titles}
    except Exception as e:
        print(f"--- Tool error: Unexpected error for r/{subreddit}: {e} ---")
        return {subreddit: [f"An unexpected error occurred while fetching from r/{subreddit}."]}

agent = Agent(
    model="gemini-2.0-flash",
    name="reddit_agent",
    description="""A specialized Reddit agent that searches for relevant posts on a given subreddit.""",
    instruction="""
        You are the Agentic AI News Scout. Your primary task is to fetch and summarize new developmnets 
            around Agentic AI.
        1. **Identify Intent:** Determine if the user is asking for Agentic AI news or related topics.
        2. **Determine Subreddit:** Identify which subreddit(s) to check. Use the specific subreddit(s) 
                if mentioned (e.g., 'AI_Agents', 'agenticaidev'). If none mentioned use default as 'AI_Agents'.
        3. **Synthesize Output:** Take the exact list of titles returned by the tool.
        4. **Format Response:** Present the information as a concise, bulleted list. Clearly state which subreddit(s) the information came from. 
                If the tool indicates an error or an unknown subreddit, report that message directly.
        5. **MUST CALL TOOL:** You **MUST** call the `get_reddit_news` tool with the identified subreddit(s).
                Do NOT generate summaries without calling the tool first.""",
    tools=[get_reddit_news]
)

root_agent = agent
