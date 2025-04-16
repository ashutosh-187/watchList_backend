from subscription import subscribe_instruments
from search_instrument import search
from redis_handler import (
    get_redis_hash,
    delete_redis_hash
)
from database import connect_with_database
from time import sleep


def add_instruments_to_watch_list(search_instrument, collection, redis_connection): 
    searched_instrument_details = search(search_instrument.upper())
    segment = searched_instrument_details.get("segment_id")
    instrument = searched_instrument_details.get("instrument_id")
    subscription_list = [
        {
            "exchangeSegment": segment,
            "exchangeInstrumentID": instrument
        }
    ]
    subscribe_instruments(subscription_list)
    redis_key = f"{segment}_{instrument}"
    data = get_redis_hash(redis_key, redis_connection)
    if len(data) == 0:
        sleep(6)
    data["name"] = search_instrument
    if not data:
        return {
            "status": "subscribed",
            "instrument_details": searched_instrument_details,
            "note": "Data not yet available in Redis"
        }
    collection.update_one(
        {"name": search_instrument},
        {
            "$set": {
                "name": search_instrument,
                "segment_id": redis_key,
            }
        },
        upsert=True
    )
    return data

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
    removed_instruments = []
    for instrument in search_instrument:
        name = instrument.get("name")
        name = name.replace(" ", "")
        result = collection.find_one(
            {
                "name": name
            }
        )
        segment_id = result.get('segment_id')
        collection.delete_one(
            {
            "name": name,
            "segment_id": segment_id
            }
        )
        redis_connection.delete(segment_id)
        removed_instruments.append(instrument)
    return {"status": "removed", "instruments": removed_instruments}

if __name__ == "__main__":
    add_instruments_to_watch_list("swiggy")