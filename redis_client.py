import redis
import os

_redis_client = None


def get_redis_client():
    global _redis_client

    if _redis_client:
        return _redis_client

    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT", 6379)

    # Redis not configured (CI / local tests)
    if not redis_host:
        return None

    _redis_client = redis.Redis(
        host=redis_host,
        port=int(redis_port),
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2
    )

    return _redis_client
