import redis
import json


# REDIS_ADDRESS = '127.0.0.1'
REDIS_ADDRESS = 'redis'
REDIS_PORT = 6379

redis_client = redis.Redis(host=REDIS_ADDRESS, port=REDIS_PORT, db=0)
redis_pb = redis_client.pubsub()
redis_pb.subscribe('fakelog')


for raw_msg in redis_pb.listen():
    if raw_msg['type'] != 'message':
        continue

    log_msg = json.loads(raw_msg['data'].decode('utf-8'))

    print(log_msg)
