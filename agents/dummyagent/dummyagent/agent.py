from google.adk.agents import Agent


def generate_response(user_input: str) -> dict:
    """Produces an appropriate response to a given user input.

    Args:
        user_input (str): What the user said.

    Returns:
        str: the appropriate response to return to the user
    """
    # return {
    #     "status": "success",
    #     "response": "You said " + str(len(user_input)) + " characters!",
    # }
    return "You said " + str(len(user_input)) + " characters!"


root_agent = Agent(
    name="responder",
    model="gemini-2.5-flash-lite",
    description=(
        "Agent to have interactions with users."
    ),
    instruction=(
        """You are a helpful agent who can reply to anything that the user says.

* Always use the `generate_response` to generate the response to be given to the user. Use the output of this tool as-is."""
    ),
    tools=[generate_response],
)
