import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def generate_access_token():
    url = os.getenv("xts_url") + "/auth/login"
    body = {
        "secretKey": os.getenv("api_secret"),
        "appKey": os.getenv("api_key"),
        "source": "WebAPI"
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=body, headers=headers)
    response_json = response.json()
    access_token = response_json.get("result", {}).get("token")
    if not access_token:
        raise ValueError("Failed to get access token from response")
    with open("access_token.json", "w") as token_file:
        json.dump({"access_token": access_token}, token_file)
    print("Access token generated :)")
    return access_token

def load_access_token():
    with open('access_token.json', 'r') as file:
        data = json.load(file)
        return data['access_token']

if __name__ == "__main__":
    generate_access_token()