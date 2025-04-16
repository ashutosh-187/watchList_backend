import socketio
import os 
from dotenv import load_dotenv
from redis_handler import (
    connect_with_redis_server,
    set_redis_hash,
    get_redis_hash
)
from get_access_token import (
    generate_access_token,
    load_access_token
)
from time import sleep

load_dotenv()

sio = socketio.Client()

def web_socket():
    token = generate_access_token()
    access_token = load_access_token()
    redis_connection = connect_with_redis_server()

    userID = os.getenv("userID")
    publishFormat = "JSON"
    broadcastFormat = "Partial"
    url = os.getenv("xts_url")

    socket_connection_url = f"{url}/?token={access_token}&userID={userID}&publishFormat={publishFormat}&broadcastMode={broadcastFormat}"

    @sio.on('connect')
    def connect(data=None):
        print("connected with websocket...")

    @sio.event
    def connect_error(data):
        print('Connection failed:', data)

    @sio.event
    def disconnect():
        print("disconnected with websocket...")

    @sio.on('1501-json-partial')
    def on_message_from_1501(data):
        if isinstance(data, str):
            web_socket_data = data.split(",")
            if "t:" in web_socket_data[0]:
                segment = web_socket_data[0].replace("t:", "")
            ltp_data = [web_socket_data[1], web_socket_data[3]]
            for data in ltp_data:
                if "ltp:" in data:
                    ltp = data.replace('ltp:', '')
                    break
            closing_data = [web_socket_data[13], web_socket_data[15]]
            for data in closing_data:
                if "c:" in data:
                    close = data.replace('c:', '')
                    break
            percentage_change_data = [web_socket_data[9], web_socket_data[11]]
            for data in percentage_change_data:
                if "pc:" in data:
                    percentage_change = data.replace('pc:', '')
                    break
            market_data = {
                "segment": segment,
                "ltp": ltp,
                "closing": close,
                "percentage_change": round(float(percentage_change), 6)
            }
            print(web_socket_data)
            sleep(6)
            set_redis_hash(segment, market_data, redis_connection)

    sio.connect(
        socket_connection_url,
        headers={},
        namespaces=None,
        transports='websocket',
        socketio_path='/apimarketdata/socket.io'
    )

    sio.wait()

if __name__ == "__main__":
    web_socket()