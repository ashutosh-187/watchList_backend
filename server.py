from flask import Flask, request, jsonify
from redis_handler import connect_with_redis_server
from database import (
    connect_with_database,
    connect_with_master_database
    )
from main import (
    add_instruments_to_watch_list,
    get_watch_list,
    remove_instruments_to_watch_list
)
from search_instrument import search
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='*')

database_collection = connect_with_database()
master_database_collection = connect_with_master_database()
redis_server_connection = connect_with_redis_server()

@app.route('/watch_list/search')
def search_instrument():
    response = search(request.args.get("search_param").upper())
    return jsonify(response)

@app.route("/watch_list/add_instrument", methods=['POST'])
def add_instrument():
    data = request.get_json()
    response = add_instruments_to_watch_list(data, database_collection, redis_server_connection)
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
