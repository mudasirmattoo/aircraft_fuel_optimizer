def generate_report(optimization_result):
    report = f"""
    Original Fuel Burn: {optimization_result['original_fuel_burn']}
    Optimized Fuel Burn: {optimization_result['optimized_fuel_burn']}
    Fuel Saved: {optimization_result['fuel_saved']} kg/min
    Optimized Route: {optimization_result['optimized_route']}
    """
    return report

