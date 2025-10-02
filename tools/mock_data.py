"""
Mock data for testing when external APIs are not available
"""

MOCK_FLIGHT_DETAILS = {
    "flight_number": "AA100",
    "departure": {
        "airport": "John F. Kennedy International Airport",
        "iata": "JFK",
        "icao": "KJFK",
        "terminal": "8",
        "gate": "12",
        "scheduled": "2025-10-02T08:00:00-04:00"
    },
    "arrival": {
        "airport": "Los Angeles International Airport",
        "iata": "LAX",
        "icao": "KLAX",
        "terminal": "4",
        "gate": "52B",
        "scheduled": "2025-10-02T11:00:00-07:00"
    },
    "aircraft": {
        "registration": "N123AA",
        "iata": "B773",
        "icao": "B777-300",
        "icao24": "A0F3B2"
    },
    "airline": {
        "name": "American Airlines",
        "iata": "AA",
        "icao": "AAL"
    },
    "flight_status": "scheduled"
}

MOCK_ROUTE = [
    {"name": "JFK", "type": "airport", "latitude": 40.6413, "longitude": -73.7781, "altitude_ft": 13},
    {"name": "JFK11", "type": "waypoint", "latitude": 40.7, "longitude": -73.8, "altitude_ft": 35000},
    {"name": "ROBER", "type": "waypoint", "latitude": 40.5, "longitude": -76.0, "altitude_ft": 37000},
    {"name": "RST", "type": "waypoint", "latitude": 39.0, "longitude": -80.5, "altitude_ft": 37000},
    {"name": "LAX", "type": "airport", "latitude": 33.9416, "longitude": -118.4085, "altitude_ft": 125}
]

MOCK_PERFORMANCE = [
    {"altitude_ft": 35000, "fuel_burn_rate_kg_per_min": 38, "max_range_nm": 6630, "cruise_speed_kts": 560},
    {"altitude_ft": 37000, "fuel_burn_rate_kg_per_min": 35, "max_range_nm": 6630, "cruise_speed_kts": 560},
    {"altitude_ft": 39000, "fuel_burn_rate_kg_per_min": 36, "max_range_nm": 6450, "cruise_speed_kts": 555}
]
