from flask import Flask, request, jsonify
import json

from db import get_db_connection
from redis_client import redis_client

app = Flask(__name__)

CACHE_TTL = 60  # seconds
CACHE_KEY_USERS = "users:all"


# -------------------------
# READ (CACHE → DB FALLBACK)
# -------------------------
def get_users():
    cached_data = redis_client.get(CACHE_KEY_USERS)

    if cached_data:
        app.logger.info("REDIS HIT: users cache")
        return json.loads(cached_data)

    app.logger.info("REDIS MISS: querying MySQL")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()

    redis_client.setex(CACHE_KEY_USERS, CACHE_TTL, json.dumps(rows))

    cursor.close()
    conn.close()

    return rows


# -------------------------
# WRITE (DB → CACHE INVALIDATE)
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

    # invalidate cache
    redis_client.delete(CACHE_KEY_USERS)


# -------------------------
# ROUTES
# -------------------------
@app.route("/", methods=["GET"])
def index():
    users = get_users()
    return jsonify(users)


@app.route("/add", methods=["POST"])
def add_user():
    data = request.json
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return {"error": "name and email required"}, 400

    create_user(name, email)
    return {"status": "user created"}, 201


# -------------------------
# ENTRYPOINT
# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
