import os 
import requests
import json
from pymongo import MongoClient
from dotenv import load_dotenv
from get_access_token import (
    load_access_token
)
from database import (
    connect_with_database,
    connect_with_master_database
)

load_dotenv()

master_connection = connect_with_master_database()

fno_header = 'ExchangeSegment|ExchangeInstrumentID|InstrumentType|Name|Description|Series|NameWithSeries|InstrumentID|PriceBand.High|PriceBand.Low|FreezeQty|TickSize|LotSize|Multiplier|UnderlyingInstrumentId|UnderlyingIndexName|ContractExpiration|StrikePrice|OptionType|DisplayName|PriceNumerator|PriceDenominator|DetailedDescription'.split('|')
eq_header = 'ExchangeSegment|ExchangeInstrumentID|InstrumentType|Name|Description|Series|NameWithSeries|InstrumentID|PriceBand.High|PriceBand.Low|FreezeQty|TickSize|LotSize|Multiplier|DisplayName|ISIN|PriceNumerator|PriceDenominator|DetailedDescription'.split('|')
    
def parse_fno_data(json_string):
    data_dict = json.loads(json_string)
    fno_header = 'ExchangeSegment|ExchangeInstrumentID|InstrumentType|Name|Description|Series|NameWithSeries|InstrumentID|PriceBand.High|PriceBand.Low|FreezeQty|TickSize|LotSize|Multiplier|UnderlyingInstrumentId|UnderlyingIndexName|ContractExpiration|StrikePrice|OptionType|DisplayName|PriceNumerator|PriceDenominator|DetailedDescription'
    headers = fno_header.split('|')
    result_lines = data_dict['result'].strip().split('\n')
    parsed_results = []
    for line in result_lines:
        values = line.split('|')
        line_dict = {}
        for i, header in enumerate(headers):
            if i < len(values):
                line_dict[header] = values[i]
        parsed_results.append(line_dict)
    return parsed_results

def master_call():
    token = load_access_token()
    exchange_segments = {
        "exchangeSegmentList": ["NSEFO", "BSEFO", "MCXFO", "NSECM", "BSECM"]
    }
    master_url = os.getenv("xts_url")+"/instruments/master"
    master_response = requests.post(master_url, json=exchange_segments)
    master_dict = parse_fno_data(master_response.text)
    master_connection.insert_many(master_dict)
    print("master data saved in database :)")

# def find_latest_expiry():
#     query = {
#         "ExchangeSegment": "MCXFO",
#         "Name": "CRUDEOIL",
#         "Series": {
#             "$nin": ["COMDTY"]
#         }
#     }
#     latest_contract = list(collection.find(query).sort("ContractExpiration", -1).limit(1))[0]
#     temp = {
#         "ExchangeInstrumentID": latest_contract["ExchangeInstrumentID"],
#         "ContractExpiration" : latest_contract['ContractExpiration'],
#         "StrikePrice": latest_contract['StrikePrice']
#     }
#     return latest_contract["ExchangeInstrumentID"]

if __name__ == "__main__":
    master_call()