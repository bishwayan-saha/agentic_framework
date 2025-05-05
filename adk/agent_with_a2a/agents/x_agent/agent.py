## Purpose:
## This file defines a simple agent that returns the current time

from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
from google.adk.runners import Runner
import tweepy
import os

load_dotenv()


def get_x_tweet_posts(handle_name: str, limit: int = 3) -> dict[str, list[str]]:
    """
    Fetches top post titles from a specified x handle using the X API.

    Args:
        handle_name: The name of the X handle to fetch posts from.
        limit: The maximum number of top posts to fetch.

    Returns:
        A dictionary with the X handlename as key and a list of
        post titles as value. Returns an error message if credentials are
        missing, the handlename is invalid, or an API error occurs.
    """

    # x_client = tweepy.Client(
    #     bearer_token=os.getenv("X_BEARER_TOKEN"),
    #     consumer_key=os.getenv("X_CONSUMER_API_KEY"),
    #     consumer_secret=os.getenv("X_CONSUMER_API_SECRET"),
    #     access_token=os.getenv("X_ACCESS_TOKEN"),
    #     access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
    # )

    auth = tweepy.OAuthHandler(
        os.getenv("X_CONSUMER_API_KEY"), os.getenv("X_CONSUMER_API_SECRET")
    )
    auth.set_access_token(os.getenv("X_ACCESS_TOKEN"), os.getenv("X_ACCESS_TOKEN_SECRET"))
    x_client = tweepy.API(auth)

    try:
        tweets = x_client.user_timeline(screen_name=handle_name, count=limit)
        titles = [tweet.full_text for tweet in tweets]
        return {handle_name: titles}
    except Exception as e:
        print(f"--- Tool error: Unexpected error for {handle_name}: {e} ---")
        return {handle_name: [f"An unexpected error occurred while fetching from {handle_name}."]}

class XAgent:

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """
        Initialize the XAgent.
        Sets up session handling, memory and runner to execute task
        """
        self._agent = self._build_agent()
        self._user_id = "remote_x_twitter_agent"
        ## Runner is used to manage the agent and its environment
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            artifact_service=InMemoryArtifactService(),  # retreive files/ docs/ artifacts
            session_service=InMemorySessionService(),  # keeps track of conversation by managing sessions
            memory_service=InMemoryMemoryService(),  # Optional: remembers past messages
        )

    def _build_agent(self) -> LlmAgent:
        """Creates and returns an LlmAgent instance"""
        return LlmAgent(
            model="gemini-1.5-flash",
            name="x_twitter_agent",
            description="""A specialized Reddit agent that searches for relevant posts on a given subreddit.""",
            instruction="""
                You are the X tweets explorer. Your primary task is to fetch new posts from a given X-handle.
                1. **Identify Intent:** Determine if the user is asking for any X posts/tweets or related topics.
                2. **Determine Subreddit:** Identify which X handle to check. If none specified, prompt the user to enter the handle name'.
                3. **Synthesize Output:** Take the exact list of titles returned by the tool.
                4. **Format Response:** Present the information as a concise, bulleted list. Clearly state which X user handle the information came from. 
                        If the tool indicates an error or an unknown handle, report that message directly.
                5. **MUST CALL TOOL:** You **MUST** call the `get_x_tweet_posts` tool with the identified X handle.
                        DO NOT generate random summaries without calling the tool first.""",
            tools=[get_x_tweet_posts],
        )

    def invoke(self, query: str, session_id: str) -> str:
        """
        Receives a user query about X user posts and returns a response
        Args:
            query (str): The query to be processed
            session_id (str): The session ID for context of grouping messages
        Returns:
            str: The response (X tweets) from the agent
        """
        session = self._runner.session_service.get_session(
            app_name=self._agent.name, user_id=self._user_id, session_id=session_id
        )

        if not session:
            session = self._runner.session_service.create_session(
                app_name=self._agent.name, user_id=self._user_id, session_id=session_id
            )

        ## Formatting user message in way the model can understand
        content = types.Content(role="user", parts=[types.Part.from_text(text=query)])

        ## Run the aget using Runner and get the response events
        events = list(
            self._runner.run(
                user_id=self._user_id, session_id=session_id, new_message=content
            )
        )

        ## Fallback response if no events are returned
        if not events or not events[-1].content or not events[-1].content.parts:
            return "No response from agent"

        ## Extract the responses text from all events and join them
        response_text = "\n".join(
            [part.text for part in events[-1].content.parts if part.text]
        )

        return response_text
