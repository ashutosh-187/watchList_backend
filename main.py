from subscription import (
    subscribe_instruments,
    unsubscribe_instruments
    )
from redis_handler import (
    get_redis_hash
)

def add_instruments_to_watch_list(data, collection, redis_connection): 
    exchange_segment = data.get('ExchangeSegment')
    exchange_instrument_id = data.get('ExchangeInstrumentID')
    name = data.get('Description')
    if exchange_segment == "NSECM":
        exchange_segment_id = '1'
    if exchange_segment == "NSEFO":
        exchange_segment_id = '2'
    if exchange_segment == "BSECM":
        exchange_segment_id = '11'
    if exchange_segment == "BSEFO":
        exchange_segment_id = '12'
    if exchange_segment == "MCXFO":
        exchange_segment_id = '51'
    subscription_list = [
        {
            "exchangeSegment": exchange_segment_id,
            "exchangeInstrumentID": exchange_instrument_id
        }
    ]
    subscribe_instruments(subscription_list)
    redis_key = f"{exchange_segment_id}_{exchange_instrument_id}"
    data = get_redis_hash(redis_key, redis_connection)
    data["name"] = data.get("Description")
    if not data:
        return {
            "status": "subscribed",
            "exchangeSegment": exchange_segment_id,
            "exchangeInstrumentID": exchange_instrument_id,
            "note": "Data not yet available in Redis"
        }
    collection.update_one(
        {"name": name},
        {
            "$set": {
                "name": name,
                "segment_id": redis_key,
            }
        },
        upsert=True
    )
    return ':)'

def get_watch_list(collection, redis_collection):
    watch_list = []
    database_data = collection.find()
    for document in database_data:
        redis_key = document.get("segment_id")
        redis_data = get_redis_hash(redis_key, redis_collection)
        redis_data['name'] = document.get('name')
        watch_list.append(redis_data)
    return watch_list

def remove_instruments_to_watch_list(search_instrument, collection, redis_connection): 
    collection.delete_one(
            {
                "segment_id": search_instrument
            }
        )
    segment, instrument = search_instrument.split("_")
    unsubscribe_instruments(
        [
            {
                "exchangeSegment": segment,
                "exchangeInstrumentID": instrument
            }
        ]
    )
    redis_connection.delete(search_instrument)
    return {"status": "removed", "instruments": search_instrument}

if __name__ == "__main__":
    add_instruments_to_watch_list("swiggy")