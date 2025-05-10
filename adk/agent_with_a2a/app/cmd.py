# =============================================================================

# This file is a command-line interface (CLI) that lets users interact with
# the TellTimeAgent running on an A2A server.
#
# It sends simple text messages (like "What time is it?") to the agent,
# waits for a response, and displays it in the terminal.
#
# This version supports:
# - basic task sending via A2AClient
# - session reuse
# - optional task history printing
# =============================================================================

import asyncclick as click
import asyncio
from uuid import uuid4
from client.client import A2AClient
from models.task import Task


YELLOW = "\033[1;33m"
RESET = "\033[0m"
PURPLE = "\033[0;35m"
BOLD = "\033[1m"
RED = "\033[0;31m"


@click.command()
@click.option(
    "--agent", default="http://localhost:10002", help="Base URL of the A2A agent server"
)
@click.option("--session", default=0, help="Session ID (use 0 to generate a new one)")
@click.option(
    "--history", is_flag=True, help="Print full task history after receiving a response"
)
async def cli(agent: str, session: str, history: bool):
    """
    CLI to send user messages to an A2A agent and display the response.

    Args:
        agent (str): The base URL of the A2A agent server (e.g., http://localhost:10002)
        session (str): Either a string session ID or 0 to generate one
        history (bool): If true, prints the full task history
    """

    # Initialize the client by providing the full POST endpoint for sending tasks
    client = A2AClient(url=f"{agent}")

    # Generate a new session ID if not provided (user passed 0)
    session_id = uuid4().hex if str(session) == "0" else str(session)

    # Start the main input loop
    while True:
        # Prompt user for input
        prompt = click.prompt(
            f"\n{RED}Press 'q' or type 'quit' to exit{RESET}\n{BOLD}{YELLOW}User{RESET}: "
        )

        if prompt.strip().lower() in [":q", "quit"]:
            break

        payload = {
            "id": uuid4().hex,
            "sessionId": session_id,
            "message": {
                "role": "user",  # The message is from the user
                "parts": [
                    {"type": "text", "text": prompt}
                ],  # Wrap user input in a text part
            },
        }

        try:
            task: Task = await client.send_task(payload)

            # Check if the agent responded (expecting at least 2 messages: user + agent)
            if task.history and len(task.history) > 1:
                reply = task.history[-1]  # Last message is usually from the agent
                print(
                    f"\n{BOLD}{PURPLE}Agent{RESET}:", reply.parts[0].text
                )  # Print agent's text reply
            else:
                print("\nNo response received.")

            # If --history flag was set, show the entire conversation history
            if history:
                print("\n========= Conversation History =========")
                for msg in task.history:
                    print(
                        f"[{msg.role}] {msg.parts[0].text}"
                    )  # Show each message in sequence

        except Exception as e:
            # Catch and print any errors (e.g., server not running, invalid response)
            print(f"\nError while sending task: {e}")


if __name__ == "__main__":
    asyncio.run(cli())
