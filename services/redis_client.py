import os
import redis


def get_redis_client():
    host = os.environ.get("REDIS_HOST")
    if not host:
        return None

    return redis.Redis(
        host=host,
        port=int(os.environ.get("REDIS_PORT", 6379)),
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )
