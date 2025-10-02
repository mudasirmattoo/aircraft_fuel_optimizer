import json
from copy import deepcopy
from typing import Dict, List, Union, Optional

def optimize_fuel_route(flight_data: Union[Dict, str]) -> Dict:
    """
    Optimize the flight route for fuel efficiency.
    
    Args:
        flight_data: Either a dictionary or JSON string containing flight data
        
    Returns:
        Dictionary containing the optimization results
    """
    # Parse input if it's a JSON string
    if isinstance(flight_data, str):
        try:
            flight_data = json.loads(flight_data)
        except json.JSONDecodeError:
            raise ValueError("Input is a malformed JSON string.")
    
    # Create a lookup dictionary for performance data for O(1) access
    performance_lookup = {
        int(perf['altitude_ft']): float(perf['fuel_burn_rate_kg_per_min'])
        for perf in flight_data['aircraft_performance']
    }
    
    if not performance_lookup:
        raise ValueError("No performance data available for optimization")
    
    # Find the most efficient altitude (lowest burn rate)
    best_altitude, best_burn_rate = min(
        performance_lookup.items(), 
        key=lambda x: x[1]
    )
    
    original_route = flight_data['route']
    optimized_route = []
    
    # Calculate original fuel burn and create optimized route in a single pass
    original_fuel_burn = 0.0
    
    for waypoint in original_route:
        # Calculate original fuel burn
        current_alt = int(waypoint['altitude'])
        current_burn = performance_lookup.get(current_alt, 0)
        original_fuel_burn += current_burn
        
        # Create optimized waypoint
        optimized_waypoint = waypoint.copy()
        
        # Don't optimize takeoff/landing waypoints
        if waypoint['waypoint'] in {flight_data['origin'], flight_data['destination']}:
            optimized_route.append(optimized_waypoint)
            continue
            
        # For en-route waypoints, use the most efficient altitude
        optimized_waypoint['altitude'] = best_altitude
        optimized_waypoint['optimized'] = current_alt != best_altitude
        optimized_route.append(optimized_waypoint)
    
    # Calculate optimized fuel burn
    optimized_fuel_burn = sum(
        best_burn_rate if wp.get('optimized', True) 
        else performance_lookup.get(int(wp['altitude']), 0)
        for wp in optimized_route
    )
    
    savings = original_fuel_burn - optimized_fuel_burn
    
    # Prepare the result
    result = {
        'original_route': original_route,
        'optimized_route': optimized_route,
        'original_fuel_burn': round(original_fuel_burn, 2),
        'optimized_fuel_burn': round(optimized_fuel_burn, 2),
        'fuel_savings': round(savings, 2),
        'savings_percentage': round((savings / original_fuel_burn * 100), 2) if original_fuel_burn > 0 else 0,
        'most_efficient_altitude': best_altitude,
        'optimization_applied': any(wp.get('optimized', False) for wp in optimized_route),
        'waypoints_optimized': sum(1 for wp in optimized_route if wp.get('optimized', False)),
        'total_waypoints': len(optimized_route)
    }
    
    return result
