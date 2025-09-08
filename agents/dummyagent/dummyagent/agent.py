import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent


def respond_to_user(user_input: str) -> dict:
    """Responds to anything the user says.

    Args:
        user_input (str): What the user said.

    Returns:
        dict: status and appropriate response to return to the user.
    """
    return {
        "status": "success",
        "response": "You said " + str(len(user_input)) + " characters!",
    }


root_agent = Agent(
    name="responder",
    model="gemini-2.0-flash",
    description=(
        "Agent to have interactions with users."
    ),
    instruction=(
        """You are a helpful agent who can  reply to anything that the user says.

* Always use the `respond_to_user` tool when replying to a user."""
    ),
    tools=[respond_to_user],
)
