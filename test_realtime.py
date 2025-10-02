import json
from agent import agent

def test_csv_flight():
    """Test with mock CSV data (FL123)"""
    print("=" * 60)
    print("TEST 1: Using CSV data (Mock Flight FL123)")
    print("=" * 60)
    flight_id = "FL123"
    input_prompt = json.dumps({"flight_id": flight_id})
    output = agent(input_prompt)
    print(output)
    print("\n")

def test_realtime_flight():
    """Test with real-time flight data (e.g., AA1004)"""
    print("=" * 60)
    print("TEST 2: Using Real-Time API (Flight AA1004)")
    print("=" * 60)
    flight_id = "AA1004"  # American Airlines flight
    input_prompt = json.dumps({"flight_id": flight_id})
    output = agent(input_prompt)
    print(output)
    print("\n")

if __name__ == "__main__":
    # Test CSV-based flight
    test_csv_flight()
    
    # Test real-time flight
    print("\nNote: For real-time test, the flight number needs to be currently active.")
    print("If AA1004 is not flying, you'll see fallback to CSV data.\n")
    # Uncomment to test real-time:
    # test_realtime_flight()
