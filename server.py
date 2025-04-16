from flask import Flask, request, jsonify
from redis_handler import connect_with_redis_server
from database import connect_with_database
from main import (
    add_instruments_to_watch_list,
    get_watch_list,
    remove_instruments_to_watch_list
)
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='*')

database_collection = connect_with_database()
redis_server_connection = connect_with_redis_server()

@app.route("/watch_list/add_instrument")
def add_instrument():
    instrument_string = request.args.get("instrument").upper()
    response = add_instruments_to_watch_list(instrument_string, database_collection, redis_server_connection)
    if len(response) == 1:
        response = add_instruments_to_watch_list(instrument_string, database_collection, redis_server_connection)
    return jsonify(response)

@app.route("/watch_list")
def watch_list():
    response = get_watch_list(database_collection, redis_server_connection)
    return jsonify(response)

@app.route("/watch_list/remove_instrument")
def remove_instrument():
    instrument_string = request.args.get("instrument").upper()
    response = remove_instruments_to_watch_list(instrument_string, database_collection, redis_server_connection)
    return jsonify(response)



if __name__ == "__main__":
    app.run(debug=True)
