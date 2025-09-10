import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams, StdioConnectionParams, StdioServerParameters


def get_mcp_toolset():
    """Returns the appropriate MCPToolset definition depending on whether we
    are developing locally or not.
    """
    is_local = os.environ.get("AGENT_IS_LOCAL", False)

    if is_local:
        conn_params = StdioConnectionParams(
            server_params=StdioServerParameters(
                command="/home/user/lab/adktraining/mcp/emt_madrid/.venv/bin/fastmcp",
                args=[
                        "run",
                        "/home/user/lab/adktraining/mcp/emt_madrid/server.py:init_server",
                        "--transport",
                        "stdio",
                ],
                # We should probably provide only a subset of these.
                env=os.environ,
            )
        )
    else:
        conn_params = StreamableHTTPConnectionParams(
            url="https://mcp-bicimad-884913148404.europe-west1.run.app/mcp",
        )

    return MCPToolset(
        connection_params=conn_params,
        # This is needed, otherwise deployment fails with Pickle serialization errors. (See https://github.com/google/adk-python/issues/1727)
        errlog=None,
    )


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
    tools=[get_mcp_toolset()],
)

bus_agent = Agent(
    name="bus_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to help users getting information about Madrid's bus network."
    ),
    instruction=(
        """You are a customer service agent for Madrid's municipal bus network.

Use the tools at your disposal to ask questions about buses, lines, stops, incidents, etc.

For any other request, inform the user that their request cannot be fulfilled.
"""
    ),
    tools=[get_mcp_toolset()],
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
* Delegate questions about Madrid's bus network to `bus_agent`.

For any other request, inform the user that their request cannot be fulfilled."""
    ),
    sub_agents=[
        bicimad_agent,
        bus_agent,
    ],
    tools=[],
)
