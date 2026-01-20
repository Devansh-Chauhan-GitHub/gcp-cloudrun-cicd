import redis
import os

redis_client = redis.Redis(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ.get("REDIS_PORT", 6379)),
    decode_responses=True,
    socket_connect_timeout=2,
    socket_timeout=2
)
