import redis
import json

client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def get_from_cache(key):
    value = client.get(key)
    if value:
        return json.loads(value)
    return None

def set_in_cache(key, value, ttl=300):
    # TTL = 300 seconds (5 minutes)
    client.setex(key, ttl, json.dumps(value))

def flush_cache():
    client.flushall()
    print("Cache flushed.")