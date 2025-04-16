import os
import requests
from dotenv import load_dotenv
from get_access_token import load_access_token

load_dotenv()

def search(search_param):
    # try:
        token = load_access_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": token 
        }
        if "nifty" in search_param or "NIFTY" in search_param or 'SENSEX' in search_param:
            index_url = os.getenv("xts_url") + "/instruments/indexlist"
            if "nifty" in search_param or "NIFTY" in search_param:
                params = {
                    "exchangeSegment": "1"
                }
            if 'SENSEX' in search_param:
                params = {
                    "exchangeSegment": "11"
                }
            index_response = requests.get(index_url, headers=headers, params=params)
            index_json = index_response.json()
            result = index_json.get("result")
            segment_id = result.get("exchangeSegment")
            index_list = result.get("indexList")
            for index in index_list:
                if f"{search_param}_" in index:
                    instrument_id = index.replace(f"{search_param}_", "")
            return {
                'name': search_param,
                'segment_id': segment_id,
                'instrument_id': instrument_id,
                'series': "Index"
            }

        search_param = search_param.replace(" ", "")
        search_url = os.getenv("xts_url") + "/search/instruments"
        params = {
            "searchString": search_param
        }
        response = requests.get(search_url, headers=headers, params=params)
        response.raise_for_status() 
        search_response = response.json().get('result')
        
        if not search_response:
            raise ValueError("No results found for the given search parameter.")
        
        search_response = search_response[0]
        
        return {
            'name': search_param,
            'segment_id': search_response.get('ExchangeSegment'),
            'instrument_id': search_response.get('ExchangeInstrumentID'),
            'series': search_response.get('Series')
        }
    # except requests.exceptions.RequestException as e:
    #     print(f"HTTP request failed: {e}")
    #     return None
    # except ValueError as e:
    #     print(f"Value error: {e}")
    #     return None
    # except Exception as e:
    #     print(f"An unexpected error occurred: {e}")
    #     return None

if __name__ == "__main__":
    result = search("NIFTY 50")
    # result = search("NIFTY IT")
    # result = search("SENSEX")
    # result = search("CRUDE OIL")
    # result = search('tata Motors')
    print(result)