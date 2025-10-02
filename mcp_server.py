from mcp.server import FastMCP
import httpx
import os
from dotenv import load_dotenv

load_dotenv()
mcp = FastMCP("Flight Weather MCP Server")

CHECKWX_API_KEY = os.getenv("CHECKWX_API_KEY")
CHECKWX_BASE_URL = "https://api.checkwx.com/metar"


@mcp.tool(description="Get aviation weather (METAR) by ICAO airport code using CheckWX")
async def get_aviation_weather(icao_code: str) -> str:
    try:
        headers = {"X-API-Key": CHECKWX_API_KEY}
        url = f"{CHECKWX_BASE_URL}/{icao_code}/decoded"
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            data = resp.json()
            
            if resp.status_code != 200:
                return f"Error: {data.get('error', 'unknown error')}"
            if "data" not in data or len(data["data"]) == 0:
                return "No METAR data found."
            
            metar = data["data"][0]
            text = metar.get("raw_text", "")
            temp_c = metar.get("temperature", {}).get("celsius")
            wind_data = metar.get("wind", {})
            wind_dir = wind_data.get("degrees")
            wind_speed = wind_data.get("speed_kph", 0)

            weather_report = f"METAR at {icao_code}: {text}. Temperature: {temp_c}°C, Wind: {wind_dir}° at {wind_speed} km/h."
            return weather_report
            
    except Exception as e:
        return f"Exception in get_aviation_weather: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="sse")
