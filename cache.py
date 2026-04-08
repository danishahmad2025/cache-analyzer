import redis
import json
from decimal import Decimal
from config import REDIS_CONFIG

client = redis.Redis(**REDIS_CONFIG, decode_responses=True)
##PostgreSQL returns Decimal type numbers which JSON can't serialize. Fix it with this custom encoder.
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def get_from_cache(key):
    value = client.get(key)
    if value:
        return json.loads(value)
    return None

def set_in_cache(key, value, ttl=300):
    client.setex(key, ttl, json.dumps(value, cls=DecimalEncoder))

def flush_cache():
    client.flushall()
    print("Cache flushed.")