import json

from db import get_db_connection
from redis_client import get_redis_client

CACHE_KEY = "users:all"
CACHE_TTL = 60


def get_users():
    redis_client = get_redis_client()

    if redis_client:
        cached = redis_client.get(CACHE_KEY)
        if cached:
            return json.loads(cached)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    if redis_client:
        redis_client.setex(CACHE_KEY, CACHE_TTL, json.dumps(rows))

    return rows


def create_user(name, email):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        (name, email),
    )
    conn.commit()

    cursor.close()
    conn.close()

    redis_client = get_redis_client()
    if redis_client:
        redis_client.delete(CACHE_KEY)
