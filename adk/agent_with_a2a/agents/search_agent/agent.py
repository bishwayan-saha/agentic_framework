from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

load_dotenv()

class SearchAgent:

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        """
        Initialize the SearchAgent.
        Sets up session handling, memory and runner to execute task
        """
        self._agent = self._build_agent()
        self._user_id = "remote_search_agent"
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
            model="gemini-2.0-flash",
            name="search_agent",
            description="""A specialized Reddit agent that searches for relevant posts on a given subreddit.""",
            instruction="""
                You are the Google Search Agent. Your primary task is to fetch news and information.
                1. **Identify Intent:** Determine if the user is asking for any real time information or
                  if you think it can be found on web / internet.
                2. **Synthesize Output:** Take all the information both structured or unstructured, returned by the tool.
                3. **Format Response:** Present the information as bulleted list. Along with the information, provide the link 
                        of the website from where the information is fetched.If the tool indicates an error 
                        or unable to understand the query, report that message directly.
                4. **MUST CALL TOOL:** You **MUST** call the `google_search` built in tool.
                        DO NOT generate random summaries or DO NOT make any assumptions without calling the tool first.""",
            tools=[google_search],
        )

    def invoke(self, query: str, session_id: str) -> str:
        """
        Receives a user query and returns a response
        Args:
            query (str): The query to be processed
            session_id (str): The session ID for context of grouping messages
        Returns:
            str: The response from the agent
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
