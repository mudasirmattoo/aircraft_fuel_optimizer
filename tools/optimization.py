import json
from copy import deepcopy

def get_fuel_burn_rate(altitude, performance_data):
    for entry in performance_data:
        if entry['altitude_ft'] == altitude:
            return entry['fuel_burn_rate_kg_per_min']
    return None

def optimize_fuel_route(flight_data):
    if isinstance(flight_data, str):
        try:
            flight_data = json.loads(flight_data)
        except json.JSONDecodeError:
            raise ValueError("Input is a malformed JSON string.")
        
    performance_data = flight_data['aircraft_performance'] 
    original_route = flight_data['route']

    original_fuel_burn = 0
    for row in original_route:
        burn_rate = get_fuel_burn_rate(row['altitude'], performance_data)
        if burn_rate:
            original_fuel_burn += burn_rate

    optimized_route = deepcopy(original_route)
    for leg in optimized_route:
        if leg['waypoint'] in ['JFK', 'LAX']:
            continue

        current_alt = leg['altitude']
        best_alt = current_alt
        min_burn_rate = get_fuel_burn_rate(current_alt, performance_data)

        for perf_rec in performance_data:
            if perf_rec['fuel_burn_rate_kg_per_min'] < min_burn_rate:
                min_burn_rate = perf_rec['fuel_burn_rate_kg_per_min']
                best_alt = perf_rec['altitude_ft']

        leg['altitude'] = best_alt

    optimized_fuel_burn = 0
    for row in optimized_route:
        burn_rate = get_fuel_burn_rate(row['altitude'], performance_data)
        if burn_rate:
            optimized_fuel_burn += burn_rate

    savings = original_fuel_burn - optimized_fuel_burn

    report = {
        "original_plan": {
            "route": original_route,
            "total_fuel_burn_kg_per_hr": original_fuel_burn
        },
        "optimized_plan": {
            "route": optimized_route,
            "total_fuel_burn_kg_per_hr": optimized_fuel_burn
        },
        "savings": {
            "fuel_saved": savings,
            "summary": f"Projected fuel savings: {savings} units by adjusting altitudes."
        }
    }
    
    return report
