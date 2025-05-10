# =============================================================================
## This file defines simple A2A server.
## - Receives task requests via POST ("/")
## - Let clients discover the agent's details via GET ("/.well-known/agent.json")
# =============================================================================

import json
from datetime import datetime

import uvicorn
from fastapi.encoders import jsonable_encoder
from models.agent import AgentCard
from models.json_rpc import InternalError, JSONRPCResponse
from models.request import A2ARequest, SendTaskRequest
from server.task_manager import TaskManager
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse


# def json_serializer(obj):
#     """
#     This function can convert Python datetime objects to ISO strings.
#     If you try to serialize a type it doesn't know, it will raise an error.
#     """
#     if isinstance(obj, datetime):
#         return obj.isoformat()
#     raise TypeError(f"Type {type(obj)} not serializable")


class A2AServer:
    def __init__(
        self,
        host="0.0.0.0",
        port=5000,
        agent_card: AgentCard = None,
        task_manager: TaskManager = None,
    ):
        """
        Constructor for our A2AServer

        Args:
            host: IP address to bind the server to (default is all interfaces)
            port: Port number to listen on (default is 5000)
            agent_card: Metadata that describes our agent (name, skills, capabilities)
            task_manager: Logic to handle the task (using Gemini agent here)
        """
        self.host = host
        self.port = port
        self.agent_card = agent_card
        self.task_manager = task_manager
        self.app = Starlette()

        self.app.add_route("/", self._handle_request, methods=["POST"])

        self.app.add_route(
            "/.well-known/agent.json", self._get_agent_card, methods=["GET"]
        )

    #  Launch the web server using uvicorn
    def start(self):
        """
        Starts the A2A server using uvicorn (ASGI web server).
        This function will block and run the server forever.
        """
        if not self.agent_card or not self.task_manager:
            raise ValueError("Agent card and task manager are required")

        uvicorn.run(self.app, host=self.host, port=self.port)

    # Return the agent’s metadata (GET request)
    def _get_agent_card(self, request: Request) -> JSONResponse:
        """
        agent discovery endpoint (GET /.well-known/agent.json)

        Returns:
            JSONResponse: Agent metadata as a dictionary
        """
        print("Publishing agent card")
        return JSONResponse(self.agent_card.model_dump(exclude_none=True))

    # handle_request(): Handle incoming POST requests for tasks
    async def _handle_request(self, request: Request):
        """
        handles task requests sent to the root path ("/").

        - 1. Parses incoming JSON
        - 2. Validates the JSON-RPC message
        - 3. For supported task types, delegates to the task manager
        - 4. Returns a response or error
        """
        try:
            # Step 1: Parse incoming JSON body
            body = await request.json()
            print(
                "\nIncoming JSON:\n", json.dumps(body, indent=2)
            )  # Log input for visibility

            # Step 2: Parse and validate request using discriminated union
            json_rpc = A2ARequest.validate_python(body)

            # Step 3: If it’s a send-task request, call the task manager to handle it
            if isinstance(json_rpc, SendTaskRequest):
                result = await self.task_manager.on_send_task(json_rpc)
            else:
                raise ValueError(f"Unsupported A2A method: {type(json_rpc)}")

            # Step 4: Convert the result into a proper JSON response
            return self._create_response(result)

        except Exception as e:
            print(f"Exception: {e}")
            return JSONResponse(
                JSONRPCResponse(
                    id=None, error=InternalError(message=str(e))
                ).model_dump(),
                status_code=400,
            )

    # Converts result object to JSONResponse
    def _create_response(self, result):
        """
        Converts a JSONRPCResponse object into a JSON HTTP response.

        Args:
            result: The response object (must be a JSONRPCResponse)

        Returns:
            JSONResponse: Starlette-compatible HTTP response with JSON body
        """
        if isinstance(result, JSONRPCResponse):
            return JSONResponse(
                content=jsonable_encoder(result.model_dump(exclude_none=True))
            )
        else:
            raise ValueError("Invalid response type")
