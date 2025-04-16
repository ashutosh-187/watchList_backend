import redis

def connect_with_redis_server():
    connection = redis.Redis(
        host = 'localhost',
        port = 6379,
        decode_responses=True
    )
    if connection.ping():
        print(":) successfully connected with redis server.")
        return connection
    else:
        print(":( failed to connected with redis server.")
        return None

def set_redis_hash(key, values, redis_server):
    redis_server.hset(str(key), mapping=values)

def get_redis_hash(key, redis_server):
    return redis_server.hgetall(str(key))

def delete_redis_hash(key, redis_server):
    redis_server.delete(str(key))
    return f"{key} deleted."


def disconnect_from_redis_server(redis_server):
    if redis_server:
        redis_server.close()
        print(":( Disconnected from Redis server.")

if __name__ == "__main__":
    redis_server = connect_with_redis_server()
    print(get_redis_hash("1_26000", redis_server).get("segment_id"))