import os
import uuid
import re
from contextlib import nullcontext
import pandas as pd
from strands.tools.mcp.mcp_client import MCPClient
from mcp.client.sse import sse_client

def parse_weather_info(weather_text: str, icao_code: str) -> dict:
    """Parse weather information from MCP response and extract key details."""
    if not weather_text or weather_text == "N/A":
        return {"status": "N/A", "summary": "No weather data available"}
    
    try:
        temp_match = re.search(r'Temperature:\s*(\d+)°C', weather_text)
        temperature = temp_match.group(1) + "°C" if temp_match else "N/A"
        
        wind_match = re.search(r'Wind:\s*(\d+)°\s*at\s*(\d+)\s*km/h', weather_text)
        wind_info = f"{wind_match.group(1)}° at {wind_match.group(2)} km/h" if wind_match else "N/A"
        
        metar_match = re.search(r'METAR\s+\w+\s+[^\n]+', weather_text)
        metar_raw = metar_match.group(0) if metar_match else "N/A"
        
        summary_parts = []
        if temperature != "N/A":
            summary_parts.append(f"Temp: {temperature}")
        if wind_info != "N/A":
            summary_parts.append(f"Wind: {wind_info}")
        
        summary = f"{icao_code}: " + ", ".join(summary_parts) if summary_parts else f"{icao_code}: Weather data available"
        
        return {
            "status": "Available",
            "summary": summary,
            "temperature": temperature,
            "wind": wind_info,
            "metar_raw": metar_raw,
            "full_report": weather_text
        }
    except Exception as e:
        return {
            "status": "Parse Error", 
            "summary": f"{icao_code}: Error parsing weather data",
            "error": str(e),
            "raw_data": weather_text
        }

def ingest_flight_data(flight_id: str) -> dict:
    flight_plan_path = 'data/flight_plan.csv'
    performance_path = 'data/aircraft_performance.csv'
    
    if not os.path.exists(flight_plan_path):
        raise FileNotFoundError(f"Flight plan data file not found: {flight_plan_path}")
    if not os.path.exists(performance_path):
        raise FileNotFoundError(f"Aircraft performance data file not found: {performance_path}")
        
    try:
        flight_plan_df = pd.read_csv(flight_plan_path)
        performance_df = pd.read_csv(performance_path)
    except Exception as e:
        raise ValueError(f"Error reading data files: {str(e)}")
    
    try:
        mcp_client = MCPClient(lambda: sse_client("http://localhost:8000/sse"))
        use_mcp = True
    except Exception as e:
        print(f"Warning: Could not initialize MCP client. Weather data will be limited. Error: {e}")
        use_mcp = False
        mcp_client = None  
        
    with nullcontext() if mcp_client is None else mcp_client:
        try:
            flight_waypoints = flight_plan_df[flight_plan_df['flight_id'] == flight_id].to_dict('records')
            if not flight_waypoints:
                raise ValueError(f"Flight ID {flight_id} not found in flight plan data")
        except Exception as e:
            raise ValueError(f"Error processing flight data: {str(e)}")
        
        aircraft_type = flight_waypoints[0].get('aircraft_type')
        if not aircraft_type or pd.isna(aircraft_type):
            raise ValueError(f"No aircraft type specified for flight {flight_id}")
            
        aircraft_performance = performance_df[performance_df['aircraft_type'] == aircraft_type]
        if aircraft_performance.empty:
            raise ValueError(f"No performance data found for aircraft type: {aircraft_type}")

        first_waypoint = flight_waypoints[0]
        full_flight_data = {
            "flight_id": flight_id,
            "origin": first_waypoint.get('origin'),
            "destination": first_waypoint.get('destination'),
            "aircraft_type": aircraft_type,
            "aircraft_performance": aircraft_performance.to_dict('records'),
            "route": []
        }

        for waypoint in flight_waypoints:
            waypoint_name = waypoint.get('waypoint', '')
            altitude_ft = waypoint.get('planned_altitude_ft')
            speed_knots = waypoint.get('planned_speed_knots')
            
            print(f"Processing waypoint: {waypoint_name} at {altitude_ft}ft, {speed_knots}kts")
            
            # Find the closest altitude in performance data if exact match not found
            try:
                if not aircraft_performance.empty and altitude_ft is not None:
                    # Get the closest altitude in performance data
                    altitude_diff = (aircraft_performance['altitude_ft'] - altitude_ft).abs()
                    closest_idx = altitude_diff.idxmin()
                    waypoint_perf = aircraft_performance.iloc[closest_idx].to_dict()
                else:
                    waypoint_perf = {}
            except Exception as e:
                print(f"Warning: Error finding performance data for altitude {altitude_ft}ft: {str(e)}")
                waypoint_perf = {}
            
            weather_data = {"status": "N/A", "summary": "No weather data available"}
            
            # Check if this waypoint has an ICAO code (4 letters, all caps)
            is_icao_code = (len(waypoint_name) == 4 and waypoint_name.isalpha() and waypoint_name.isupper())
            
            # Fetch weather for ICAO codes (airports) or major waypoints
            if (waypoint_name in [full_flight_data['origin'], full_flight_data['destination']] or is_icao_code) and use_mcp:
                try:
                    print(f"Fetching weather for {waypoint_name}")
                    tool_use_id = str(uuid.uuid4())
                    weather_response = mcp_client.call_tool_sync(
                        name="get_aviation_weather", 
                        arguments={"icao_code": waypoint_name},
                        tool_use_id=tool_use_id
                    )
                    if weather_response.get("isError") is False:
                        content = weather_response.get("content", [])
                        if content and len(content) > 0:
                            weather_text = content[0].get("text", "N/A")
                            
                            # Parse weather information for better display
                            weather_data = parse_weather_info(weather_text, waypoint_name)
                            print(f"Weather retrieved for {waypoint_name}: {weather_data['summary']}")
                        else:
                            weather_data = {"status": "No data", "summary": f"No weather data available for {waypoint_name}"}
                    else:
                        error_msg = weather_response.get("content", [{}])[0].get("text", "Unknown error")
                        weather_data = {"status": "Error", "summary": f"Weather fetch failed: {error_msg}"}
                except Exception as e:
                    print(f"Error fetching weather for {waypoint_name}: {str(e)}")
                    weather_data = {"status": "Error", "summary": f"Weather service error: {str(e)}"}

            waypoint_data = {
                "waypoint": waypoint_name,
                "altitude": altitude_ft,
                "speed_knots": speed_knots,
                "fuel_burn_rate": waypoint_perf.get('fuel_burn_rate_kg_per_min', 0) if waypoint_perf else 0,
                "weather": weather_data
            }
            full_flight_data["route"].append(waypoint_data)

    # Verify we have route data before returning
    if not full_flight_data["route"]:
        raise ValueError(f"No valid route data could be generated for flight {flight_id}")
        
    print(f"Successfully processed {len(full_flight_data['route'])} waypoints for flight {flight_id}")
    return full_flight_data
