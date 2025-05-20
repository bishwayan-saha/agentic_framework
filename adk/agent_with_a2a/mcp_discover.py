import json
import os


class MCPToolDiscovery:

    def __init__(self, config_file: str) -> None:

        if config_file:
            self._config_file = config_file
        else:
            self._config_file = os.path.join(
                os.path.dirname(__file__), "mcp_config.json"
            )
        self._config = self._load_config()

    def _load_config(self):
        try:
            with open(self._config_file, "r") as file:
                data = json.load(file)
            return data
        except Exception as e:
            print(e)

    def list_servers(self):
        print(f" MCOP Servers{self._config.get("mcpServers", {})}")
        return self._config.get("mcpServers", {})
