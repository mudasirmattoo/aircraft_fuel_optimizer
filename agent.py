from strands import Agent, tool
from tools.ingestion import ingest_flight_data
from tools.optimization import optimize_fuel_route
from tools.reporting import generate_report
from strands.models import BedrockModel

bedrock_model = BedrockModel(
    model_id="arn:aws:bedrock:us-east-1:776926034800:inference-profile/global.anthropic.claude-sonnet-4-20250514-v1:0",
    temperature=0.3,
    top_p=0.8,
    region_name="us-east-1",
)

tools = [
    tool(name = "IngestFlightData", func= ingest_flight_data),
    tool(name = "OptimizeFuelRoute", func= optimize_fuel_route),
    tool(name = "GenerateReport", func= generate_report),
]

system_prompt = """
You are an airline fuel optimization agent.
Use the given tools to fetch and analyze flight and weather data,
optimize the fuel route, and produce a detailed efficiency report.
"""

agent = Agent(
    system_prompt=system_prompt,
    tools=tools,
    model=bedrock_model,
)