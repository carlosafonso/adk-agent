import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
import os


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
            connection_params=StdioServerParameters(
                command='python',
                args=['../bicimad_mcp/server.py'],
                env={
                    "GOOGLE_MAPS_API_KEY": os.environ["GOOGLE_MAPS_API_KEY"],
                    "BICIMAD_API_ACCESS_TOKEN": os.environ["BICIMAD_API_ACCESS_TOKEN"],
                }
            )
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
