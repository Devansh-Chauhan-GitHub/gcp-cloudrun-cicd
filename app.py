from flask import Flask, request, jsonify
import json
import logging

from db import get_db_connection
from redis_client import get_redis_client

# -------------------------
# APP SETUP
# -------------------------
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# -------------------------
# CACHE CONFIG
# -------------------------
CACHE_TTL = 60  # seconds
CACHE_KEY_USERS = "users:all"


# -------------------------
# READ (REDIS → MYSQL)
# -------------------------
def get_users():
    redis_client = get_redis_client()

    if redis_client:
        try:
            cached = redis_client.get(CACHE_KEY_USERS)
            if cached:
                app.logger.info("REDIS HIT: users cache")
                return json.loads(cached)

            app.logger.info("REDIS MISS: querying MySQL")
        except Exception as e:
            app.logger.error(f"REDIS ERROR: {e}")

    # MySQL fallback (source of truth)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Populate cache (best effort)
    if redis_client:
        try:
            redis_client.setex(
                CACHE_KEY_USERS,
                CACHE_TTL,
                json.dumps(rows)
            )
            app.logger.info("REDIS SET: users cache populated")
        except Exception as e:
            app.logger.error(f"REDIS SET FAILED: {e}")

    return rows


# -------------------------
# WRITE (MYSQL → CACHE INVALIDATE)
# -------------------------
def create_user(name, email):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO users (name, email) VALUES (%s, %s)",
        (name, email)
    )

    conn.commit()
    cursor.close()
    conn.close()

    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.delete(CACHE_KEY_USERS)
            app.logger.info("REDIS DELETE: users cache invalidated")
        except Exception as e:
            app.logger.error(f"REDIS DELETE FAILED: {e}")


# -------------------------
# ROUTES
# -------------------------
@app.route("/", methods=["GET"])
def index():
    return jsonify(get_users())


@app.route("/add", methods=["POST"])
def add_user():
    data = request.json or {}

    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return {"error": "name and email required"}, 400

    create_user(name, email)
    return {"status": "user created"}, 201


# -------------------------
# LOCAL ENTRYPOINT
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
