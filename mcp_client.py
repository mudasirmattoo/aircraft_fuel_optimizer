from mcp.client.sse import sse_client
from strands.tools.mcp.mcp_client import MCPClient
from strands import Agent

def run():
    sse_client_transport = lambda: sse_client("http://localhost:8000/sse")
    mcp_client = MCPClient(sse_client_transport)

    print("Connecting to MCP server...")
    with mcp_client:
        tools = mcp_client.list_tools_sync()
        print("Available MCP Tools:", [str(t) for t in tools])

        agent = Agent(tools=tools)

        print("Calling get_aviation_weather...")
        weather_response = agent("get_aviation_weather icao_code=VIDP")
        print("Weather response:", weather_response)

        print("Calling get_flight_status...")
        flight_response = agent("get_flight_status flight_number=AI101")
        print("Flight status response:", flight_response)

if __name__ == "__main__":
    run()
