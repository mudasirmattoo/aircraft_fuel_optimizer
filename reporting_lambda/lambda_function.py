import json
import os
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

def get_live_weather(station_code: str, api_key: str):
    if not api_key:
        print("API key not configured")
        return {}

    headers = {'X-API-Key': api_key}
    url = f'https://api.checkwx.com/metar/{station_code}/decoded'
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json().get('data', [{}])[0]
        
        wind = data.get('wind', {})
        return {
            "wind_direction": wind.get('degrees'),
            "wind_speed_knots": wind.get('speed_kts')
        }
    except requests.exceptions.RequestException as e:
        print(f"Could not fetch weather for {station_code}: {e}")
        return {}
    except (KeyError, IndexError):
        print(f"Unexpected JSON structure for {station_code}.")
        return {}

def lambda_handler(event, context):
    flight_id = event['flight_id']
    
    api_key = os.environ.get('CHECKWX_API_KEY')

    flight_plan_df = pd.read_csv('data/flight_plan.csv')
    performance_df = pd.read_csv('data/aircraft_performance.csv')

    flight = flight_plan_df[flight_plan_df['flight_id'] == flight_id].to_dict('records')

    if not flight:
        raise ValueError(f"Flight with ID '{flight_id}' not found")
    
    full_flight_data = {
        "flight_id": flight_id,
        "origin": flight[0]['origin'],
        "destination": flight[0]['destination'],
        "aircraft_performance": performance_df.to_dict('records'),
        "route": []
    }

    for row in flight:
        waypoint_name = row['waypoint']
        live_weather = get_live_weather(waypoint_name, api_key)
        
        row_data = {
            "waypoint": waypoint_name,
            "altitude": row['planned_altitude_ft'],
            "speed": row['planned_speed_knots'],
            "weather": live_weather
        }
        full_flight_data["route"].append(row_data)
        
    return full_flight_data