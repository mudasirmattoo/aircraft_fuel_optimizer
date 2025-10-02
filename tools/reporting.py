def generate_report(optimization_result):
    try:
        original_burn = optimization_result['original_plan']['total_fuel_burn_kg_per_hr']
        optimized_burn = optimization_result['optimized_plan']['total_fuel_burn_kg_per_hr']
        fuel_saved = optimization_result['savings']['fuel_saved']
        
        original_altitudes = [str(wp['altitude']) for wp in optimization_result['original_plan']['route']]
        optimized_altitudes = [str(wp['altitude']) for wp in optimization_result['optimized_plan']['route']]
        
        weather_info = []
        for waypoint in optimization_result['original_plan']['route']:
            weather = waypoint.get('weather', {})
            if isinstance(weather, dict) and weather.get('status') == 'Available':
                weather_info.append(f"- **{waypoint['waypoint']}**: {weather.get('summary', 'Weather available')}")
        
        weather_section = ""
        if weather_info:
            weather_section = f"""
### Weather Conditions:
{chr(10).join(weather_info)}
"""
        
        report = f"""## Fuel Optimization Analysis Complete for Flight

### Flight Details:
- **Original Fuel Burn Rate**: {original_burn} kg/hr
- **Optimized Fuel Burn Rate**: {optimized_burn} kg/hr
- **Fuel Savings**: {fuel_saved} kg/hr

### Altitude Adjustments:
- **Original Altitudes (ft)**: {' → '.join(original_altitudes)}
- **Optimized Altitudes (ft)**: {' → '.join(optimized_altitudes)}
{weather_section}
### Optimization Summary:
{optimization_result['savings']['summary']}
"""
        return report
        
    except KeyError as e:
        error_msg = f"Error generating report - missing data: {str(e)}"
        print(f"Debug - optimization_result keys: {list(optimization_result.keys())}")
        if 'original_plan' in optimization_result:
            print(f"Debug - original_plan keys: {list(optimization_result['original_plan'].keys())}")
        return f"Error generating report: {error_msg}"

