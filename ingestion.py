import pandas as pd
import json

def load_flight_data(flight_id:str):
    flight_plan_df = pd.read_csv('data/flight_plan.csv')
    performance_df = pd.read_csv('data/aircraft_performance.csv')
    with open('data/mock_weather.json', 'r') as file:
        weather_data = json.load(file)

    flight = flight_plan_df[flight_plan_df['flight_id'] == flight_id].to_dict('records')

    if not flight:
        print(f"Flight with ID '{flight_id}' not found")
        return None
    
    full_flight_data = {
        "flight_id": flight_id,
        "origin": flight[0]['origin'],
        "destination": flight[0]['destination'],
        "aircraft_performance": performance_df.to_dict('records'),
        "route": []
    }

    for row in flight:
        waypoint_name = row['waypoint']
        row_data = {
            "waypoint": waypoint_name,
            "altitude": row['planned_altitude_ft'],
            "speed": row['planned_speed_knots'],
            "weather": weather_data.get(waypoint_name, {})
        }
        full_flight_data["route"].append(row_data)
        return full_flight_data
    
if __name__ == "__main__":
    flight_data = load_flight_data('FL123')
    if flight_data:
        print(json.dumps(flight_data, indent=2))
