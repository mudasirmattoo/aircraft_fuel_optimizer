import build_mcp_weather.lambda_mcp_weather as lambda_mcp_weather
import os
from dotenv import load_dotenv

load_dotenv()  # Load env vars from .env

test_event = {"icao": "KJFK"}

response = lambda_mcp_weather.lambda_handler(test_event, None)

print(response)
