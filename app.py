import os
from flask import Flask
import mysql.connector


app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),   # private IP of VM
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
    )


@app.route("/")
def show_users():
    # If DB env vars are missing, return a safe response (CI mode)
    if not os.environ.get("DB_HOST"):
        return "CI mode: DB not configured", 200

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    output = "<h1>Users from MySQL</h1><ul>"
    for row in rows:
        output += f"<li>{row[0]} - {row[1]} ({row[2]})</li>"
    output += "</ul>"

    return output


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
