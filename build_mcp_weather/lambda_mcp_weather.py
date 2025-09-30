import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()  
api_key = os.getenv("CHECKWX_API_KEY")

def lambda_handler(event, context):
    icao = event.get("icao")
    if not icao:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required 'icao' parameter"})
        }

    icao = icao.lower()

    headers = {"X-API-Key": api_key}
    url = f"https://api.checkwx.com/metar/{icao}/decoded"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data and "data" in data and len(data["data"]) > 0:
            metar_report = data["data"][0].get("raw_text", "No METAR raw text")
        else:
            metar_report = "No METAR data found"
        
        return {
            "statusCode": 200,
            "body": json.dumps({"icao": icao, "metar": metar_report})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
