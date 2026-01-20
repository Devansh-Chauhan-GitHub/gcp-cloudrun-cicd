import json
import logging

from db import get_db_connection
from redis_client import get_redis_client

CACHE_KEY = "users:all"
CACHE_TTL = 60

logger = logging.getLogger(__name__)


def get_users():
    redis_client = get_redis_client()

    # 1️⃣ Try Redis first
    if redis_client:
        cached = redis_client.get(CACHE_KEY)
        if cached:
            logger.info("REDIS HIT: users cache")
            return json.loads(cached)

    logger.info("REDIS MISS: querying MySQL")

    # 2️⃣ Fallback to MySQL
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # 3️⃣ Populate Redis cache
    if redis_client:
        redis_client.setex(
            CACHE_KEY,
            CACHE_TTL,
            json.dumps(rows)
        )
        logger.info("REDIS SET: users cache populated")

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

    # 4️⃣ Invalidate cache after write
    redis_client = get_redis_client()
    if redis_client:
        redis_client.delete(CACHE_KEY)
        logger.info("REDIS DELETE: users cache invalidated")
