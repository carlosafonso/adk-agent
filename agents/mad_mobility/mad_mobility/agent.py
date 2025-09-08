from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams

bicimad_agent = Agent(
    name="bicimad_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to help users using BiciMad, Madrid's municipal bike rental service."
    ),
    instruction=(
        """You are a customer service agent for BiciMad, Madrid's municipal bike rental service.

Use the tools at your disposal to ask questions about bikes and bike stations in the system.

For any other request, inform the user that their request cannot be fulfilled.
"""
    ),
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://mcp-bicimad-884913148404.europe-west1.run.app/mcp",
            ),
            # This is needed, otherwise deployment fails with Pickle serialization errors. (See https://github.com/google/adk-python/issues/1727)
            errlog=None,
        )
    ],
)

root_agent = Agent(
    name="mad_mobility_agent",
    model="gemini-2.0-flash",
    description=(
        "Assists users with navigating the city of Madrid."
    ),
    instruction=(
        """You are a helpful agent who can help answer users' questions about mobility within the city of Madrid.

* Delegate BiciMad (Madrid's municipal bike rental service) inquiries to `bicimad_agent`.

For any other request, inform the user that their request cannot be fulfilled."""
    ),
    sub_agents=[
        bicimad_agent,
    ],
    tools=[],
)
