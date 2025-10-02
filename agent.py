from strands import Agent, tool
from tools.ingestion import ingest_flight_data
from tools.optimization import optimize_fuel_route
from tools.reporting import generate_report
from strands.models import BedrockModel
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.sse import sse_client

bedrock_model = BedrockModel(
    model_id="arn:aws:bedrock:us-east-1:776926034800:inference-profile/global.anthropic.claude-sonnet-4-20250514-v1:0",
    temperature=0.3,
    top_p=0.8,
    region_name="us-east-1",
)

local_tools = [
    tool(name="IngestFlightData", func=ingest_flight_data),
    tool(name="OptimizeFuelRoute", func=optimize_fuel_route),
    tool(name="GenerateReport", func=generate_report),
]

system_prompt = """
You are an airline fuel optimization agent.
Use the given tools to fetch and analyze flight and weather data,
optimize the fuel route, and produce a detailed efficiency report.
"""

# Initialize MCP client and tools
mcp_client = None
mcp_tools = []

# Try to initialize MCP client and get weather tools
try:
    mcp_client = MCPClient(lambda: sse_client("http://localhost:8000/sse"))
    mcp_client.__enter__()  # Manually enter the context
    mcp_tools = mcp_client.list_tools_sync()
    print(f"Successfully connected to MCP server. Loaded {len(mcp_tools)} MCP tools.")
except Exception as e:
    print(f"Warning: Could not connect to MCP server. Weather data will not be available. Error: {e}")
    mcp_client = None

# Always include local tools, add MCP tools if available
all_tools = local_tools + mcp_tools

# Initialize the agent with all available tools
agent = Agent(
    system_prompt=system_prompt,
    tools=all_tools,
    model=bedrock_model,
)

# Ensure MCP client is properly closed on program exit
import atexit
if mcp_client is not None:
    atexit.register(lambda: mcp_client.__exit__(None, None, None))