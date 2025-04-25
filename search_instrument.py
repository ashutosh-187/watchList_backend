import re
import os
import json
import requests
from pymongo import MongoClient
from dotenv import load_dotenv
from database import connect_with_master_database
from get_access_token import load_access_token
from datetime import datetime

load_dotenv()

master_collection = connect_with_master_database()

def get_nearest_expiry_contracts(contracts):
    
    now = datetime.now()
    nearest_date = None
    nearest_contracts = []
    
    # Single pass: find the nearest >now expiration, collect all with that date
    for c in contracts:
        # parse the ISO‐format date
        exp = datetime.fromisoformat(c['ContractExpiration'])
        if exp <= now:
            continue
        
        if (nearest_date is None) or (exp < nearest_date):
            nearest_date = exp
            nearest_contracts = [c]
        elif exp == nearest_date:
            nearest_contracts.append(c)
    
    # If nothing found, bail out
    if not nearest_contracts:
        return []
    
    # From the nearest‐expiry pool, pick one Call and one Put
    calls = [c for c in nearest_contracts if c['Description'].endswith('CE')]
    puts  = [c for c in nearest_contracts if c['Description'].endswith('PE')]
    
    result = []
    if calls:
        result.append(calls[0])
    if puts:
        result.append(puts[0])
    return result

def search_future(search_param):
    term = search_param.upper().strip()
    symbol = re.sub(r"FUT", "", term).strip()
    pattern = rf".*(?:{re.escape(symbol)}.*FUT|FUT.*{re.escape(symbol)}).*"
    regex = {"$regex": pattern, "$options": "i"}
    pipeline = [
        {
            "$match": {
                "$or": [
                    {"displayName": regex},
                    {"Description": regex}
                ]
            }
        },
        {"$sort": {"ContractExpiration": 1}},
        {"$limit": 3},
        {"$addFields": {"expiry": "$ContractExpiration"}},
        {"$project": {"_id": 0}}
    ]
    return list(master_collection.aggregate(pipeline))

def get_quotes(quote_list, strike_distance):
    access_token = load_access_token()
    body = {
        "instruments": quote_list,
        "xtsMessageCode": 1501,
        "publishFormat": "JSON"
    }
    headers = {
            "Content-Type": "application/json",
            "Authorization": access_token 
    }
    subscription_url = os.getenv("xts_url")+"/instruments/quotes"
    response = requests.post(subscription_url, json=body, headers=headers).text
    response_dict = json.loads(response)
    quotes_data = json.loads(response_dict['result']['listQuotes'][0])
    last_traded_price = quotes_data['LastTradedPrice']
    atm = round(last_traded_price/strike_distance)*strike_distance
    return atm

def search(search_param):
    search_result = search_future(search_param)
    if "NIFTY" in search_param and len(search_param) <= 5:
        print("Inside NIFTY BLOCK")
        get_atm = get_quotes(
            [
                {
                    "exchangeSegment": 1,
                    "exchangeInstrumentID": 26000
                }
            ],
            50
        )
        strike_range = [get_atm - 50 * i for i in range(3, 0, -1)] + [get_atm + 50 * i for i in range(4)]
        for strike in strike_range:
            options_arr = list(master_collection.find(
                {
                    "ExchangeSegment": "NSEFO",
                    "Name": "NIFTY",
                    "Series": "OPTIDX",
                    "StrikePrice": str(strike)
                }, 
                {
                    "_id": 0
                }
            ))
            search_result.extend(get_nearest_expiry_contracts(options_arr))
        
    elif "BANKNIFTY" in search_param:
        print("Inside BANKNIFTY Block")
        get_atm = get_quotes(
                [
                    {
                        "exchangeSegment": 1,
                        "exchangeInstrumentID": 26001
                    }
                ],
                100
            )
        strike_range = [get_atm - 100 * i for i in range(3, 0, -1)] + [get_atm + 100 * i for i in range(4)]
        for strike in strike_range:
            options_arr = list(master_collection.find(
                {
                    "ExchangeSegment": "NSEFO",
                    "Name": "BANKNIFTY",
                    "Series": "OPTIDX",
                    "StrikePrice": str(strike)
                }, 
                {
                    "_id": 0
                }
            ))
            search_result.extend(get_nearest_expiry_contracts(options_arr))
    elif "SENSEX" in search_param:
        print("Inside SENSEX Block")
        get_atm = get_quotes(
                [
                    {
                        "exchangeSegment": 11,
                        "exchangeInstrumentID": 26065
                    }
                ],
                100
            )
        strike_range = [get_atm - 100 * i for i in range(3, 0, -1)] + [get_atm + 100 * i for i in range(4)]
        for strike in strike_range:
            options_arr = list(master_collection.find(
                {
                    "ExchangeSegment": "BSEFO",
                    "Name": "SENSEX",
                    "Series": "IO",
                    "StrikePrice": str(strike)
                }, 
                {
                    "_id": 0
                }
            ))
            search_result.extend(get_nearest_expiry_contracts(options_arr))
    
    return search_result




if __name__ == "__main__":
    # result = search("NIFTY 50")
    # result = search("NIFTY 24Apr2025 CE 23300")
    # result = search("BANKNIFTY 24Apr2025 PE 53000")
    # result = search("SENSEX 22Apr2025 CE 77000")
    # result = search("CRUDEOIL 16JUN2025 CE 7150")
    # result = search("Titan")
    # print(result)
    # result = search("BHARATFORG25APR25MAYFUT")
    # result = search('GOLDM 25JUN2025 CE 97100')
    # result = search('GOLDM05')
    # result = search('NIFTYFUT')
    # print(search_future("NIFTYFUT"))          # base symbol only
    # print(search("FUTNIFTY"))       # FUT prefixed
    # result = search("BANKNIFTYFUT")       # FUT suffixed
    # print(search("BHARATFORG"))  # full contract name
    # print(search_future("SENSEX"))
    # print(result)
    print(search("NIFTY APR"))
