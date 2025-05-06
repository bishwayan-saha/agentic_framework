from typing import List
from models.agent import AgentCard
import os
import json
import logging
import httpx

logger = logging.getLogger(__name__)

class DiscoveryClient:
    """
        Discover A2A agents by reading a registry file of agent server URLs and querying
        each one's /.well-known/agent.json endpoint to retrieve an AgentCard.

        Attributes:
            registry_path (str): The path to the registry file containing a list of agent server URLs.
            base_urls (list[str]): A list of agent server URLs to query.
    """

    def __init__(self, registry_path: str):
        if registry_path:
            self.registry_path = registry_path
        else:
            self.registry_path = os.path.join(os.path.dirname(__file__), "registry.json")

        self.base_urls = self._loaded_registry()

    def _loaded_registry(self) -> List[str]:
        """
        Load and parse the registry JSON file into a list of URLs.

        Returns:
            List[str]: The list of agent base URLs, or empty list on error.
        """
        try:
            with open(self.registry_path, "r") as f:
                url_list = json.load(f)
            return url_list
        except FileNotFoundError:
            logger.info(f"Registry file not found at {self.registry_path}")
            return []
        except json.JSONDecodeError:
            logger.info(f"Invalid JSON in registry file at {self.registry_path}")
            return []

    async def fetch_agent_cards(self) -> List[AgentCard]:
        """
        Asynchronously fetch the discovery endpoint from each registered URL
        and parse the returned JSON into AgentCard objects.

        Returns:
            List[AgentCard]: Successfully retrieved agent cards.
        """
        agent_cards: List[AgentCard] = []

        async with httpx.AsyncClient() as client:
            for base_url in self.base_urls:
                try:
                    url = f"{base_url.rstrip("/")}/.well-known/agent.json"
                    print(url)
                    response = await client.get(url)
                    response.raise_for_status()
                    card = AgentCard.model_validate(response.json())
                    agent_cards.append(card)
                except Exception:
                    logger.info(f"Error occurred while fetching well known url at {url}")

        return agent_cards
