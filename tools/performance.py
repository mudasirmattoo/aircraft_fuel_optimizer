"""
Real-time Aircraft Performance Module using OpenAP
Provides fuel burn rates and performance data for various aircraft types
"""

from openap import FuelFlow, prop
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AircraftPerformance:
    """
    Real-time aircraft performance calculator using OpenAP library
    """
    
    def __init__(self, aircraft_type: str):
        """
        Initialize performance calculator for a specific aircraft type
        
        Args:
            aircraft_type: ICAO aircraft type code (e.g., 'A320', 'B737', 'B777')
        """
        self.aircraft_type = self._normalize_aircraft_type(aircraft_type)
        
        try:
            # Initialize OpenAP fuel flow model
            self.fuel_model = FuelFlow(ac=self.aircraft_type)
            
            # Get aircraft properties
            self.aircraft_data = prop.aircraft(ac=self.aircraft_type)
            
            logger.info(f"✓ Loaded OpenAP performance data for {self.aircraft_type}")
        except Exception as e:
            logger.error(f"Error loading OpenAP data for {aircraft_type}: {str(e)}")
            raise ValueError(f"Aircraft type {aircraft_type} not supported by OpenAP")
    
    def _normalize_aircraft_type(self, aircraft_type: str) -> str:
        """
        Normalize aircraft type codes to OpenAP format
        
        Common mappings:
        - 'B737' -> 'B737'
        - '737' -> 'B737'
        - 'A320' -> 'A320'
        - '320' -> 'A320'
        """
        aircraft_type = aircraft_type.upper().strip()
        
        # Map common variations
        mappings = {
            '737': 'B738',  # Boeing 737-800 (most common variant)
            'B737': 'B738',
            '738': 'B738',
            '320': 'A320',
            'A320': 'A320',
            '321': 'A321',
            'A321': 'A321',
            '777': 'B77W',  # Boeing 777-300ER
            'B777': 'B77W',
            '787': 'B788',  # Boeing 787-8
            'B787': 'B788',
        }
        
        return mappings.get(aircraft_type, aircraft_type)
    
    def get_fuel_flow_at_altitude(
        self, 
        altitude_ft: int, 
        mass_kg: Optional[int] = None,
        tas_kts: Optional[int] = None,
        vertical_speed_fpm: int = 0
    ) -> float:
        """
        Calculate fuel flow at a specific altitude and conditions
        
        Args:
            altitude_ft: Altitude in feet
            mass_kg: Aircraft mass in kg (uses typical cruise mass if not provided)
            tas_kts: True airspeed in knots (uses typical cruise speed if not provided)
            vertical_speed_fpm: Vertical speed in feet per minute (0 for cruise)
        
        Returns:
            Fuel flow in kg/s
        """
        # Use typical values if not provided
        if mass_kg is None:
            mass_kg = int(self.aircraft_data['limits']['MTOW'] * 0.75)  # 75% of MTOW
        
        if tas_kts is None:
            # Typical cruise speed
            tas_kts = int(self.aircraft_data['cruise']['mach'] * 666)  # Rough conversion
        
        try:
            # Calculate fuel flow using OpenAP
            fuel_flow_kg_s = self.fuel_model.enroute(
                mass=mass_kg,
                tas=tas_kts,
                alt=altitude_ft,
                vs=vertical_speed_fpm
            )
            
            return fuel_flow_kg_s
        except Exception as e:
            logger.error(f"Error calculating fuel flow: {str(e)}")
            return 0.0
    
    def get_performance_profile(self, altitudes: List[int]) -> List[Dict]:
        """
        Get fuel burn performance across multiple altitudes
        
        Args:
            altitudes: List of altitudes in feet
        
        Returns:
            List of dicts with altitude and fuel flow data
        """
        profile = []
        
        for altitude in altitudes:
            fuel_flow_kg_s = self.get_fuel_flow_at_altitude(altitude)
            fuel_flow_kg_min = fuel_flow_kg_s * 60
            fuel_flow_kg_hr = fuel_flow_kg_s * 3600
            
            profile.append({
                'altitude_ft': altitude,
                'fuel_flow_kg_s': round(fuel_flow_kg_s, 4),
                'fuel_flow_kg_min': round(fuel_flow_kg_min, 2),
                'fuel_flow_kg_hr': round(fuel_flow_kg_hr, 2),
                'source': 'OpenAP'
            })
        
        return profile
    
    def get_aircraft_specs(self) -> Dict:
        """
        Get aircraft specifications from OpenAP database
        
        Returns:
            Dictionary with aircraft specifications
        """
        return {
            'aircraft_type': self.aircraft_type,
            'engine_type': self.aircraft_data.get('engine', {}).get('type', 'N/A'),
            'number_of_engines': self.aircraft_data.get('engine', {}).get('number', 'N/A'),
            'mtow_kg': self.aircraft_data.get('limits', {}).get('MTOW', 'N/A'),
            'max_payload_kg': self.aircraft_data.get('limits', {}).get('MPL', 'N/A'),
            'max_fuel_kg': self.aircraft_data.get('limits', {}).get('MFC', 'N/A'),
            'cruise_mach': self.aircraft_data.get('cruise', {}).get('mach', 'N/A'),
            'cruise_altitude_ft': self.aircraft_data.get('cruise', {}).get('height', 'N/A'),
        }


def get_available_aircraft() -> List[str]:
    """
    Get list of available aircraft types in OpenAP database
    
    Returns:
        List of aircraft ICAO codes
    """
    try:
        # OpenAP provides a list of supported aircraft
        from openap import prop
        aircraft_list = prop.available_aircraft()
        return sorted(aircraft_list)
    except Exception as e:
        logger.error(f"Error getting aircraft list: {str(e)}")
        return []


# Example usage
if __name__ == "__main__":
    # Test with Boeing 737
    print("Testing OpenAP Performance Module")
    print("=" * 60)
    
    aircraft = AircraftPerformance('B737')
    
    # Get aircraft specs
    specs = aircraft.get_aircraft_specs()
    print("\nAircraft Specifications:")
    for key, value in specs.items():
        print(f"  {key}: {value}")
    
    # Get performance at different altitudes
    print("\nFuel Flow at Different Altitudes:")
    altitudes = [10000, 20000, 30000, 35000, 37000, 40000]
    profile = aircraft.get_performance_profile(altitudes)
    
    for p in profile:
        print(f"  {p['altitude_ft']:5d} ft: {p['fuel_flow_kg_min']:6.2f} kg/min  ({p['fuel_flow_kg_hr']:7.2f} kg/hr)")
    
    print("\nAvailable aircraft in OpenAP:")
    available = get_available_aircraft()
    print(f"  Total: {len(available)} aircraft types")
    print(f"  Examples: {', '.join(available[:10])}")
