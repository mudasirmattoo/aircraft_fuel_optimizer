import json
from agent import agent

def main():
    flight_id = "FL123" 
    input_prompt = json.dumps({"flight_id": flight_id})
    output = agent(input_prompt)
    print(output)

if __name__ == "__main__":
    main()