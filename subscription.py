import os
import requests
from dotenv import load_dotenv
from get_access_token import (
    load_access_token
)
from redis_handler import set_redis_hash

load_dotenv()

def subscribe_instruments(subscription_list):
    access_token = load_access_token()
    body = {
        "instruments": subscription_list,
        "xtsMessageCode": 1501
    }
    headers = {
            "Content-Type": "application/json",
            "Authorization": access_token 
    }
    subscription_url = os.getenv("xts_url")+"/instruments/subscription"
    response = requests.post(subscription_url, json=body, headers=headers)
    return response.text

def unsubscribe_instruments(unsubscription_list):
    access_token = load_access_token()
    body = {
        "instruments": unsubscription_list,
        "xtsMessageCode": 1501
    }
    headers = {
            "Content-Type": "application/json",
            "Authorization": access_token 
    }
    subscription_url = os.getenv("xts_url")+"/instruments/subscription"
    response = requests.put(subscription_url, json=body, headers=headers)
    return response.text

if __name__ == "__main__":
    arr = [
        {
            "exchangeSegment": 1,
            "exchangeInstrumentID": 26001
        },
    ]
    subscribe_instruments(subscription_list=arr)