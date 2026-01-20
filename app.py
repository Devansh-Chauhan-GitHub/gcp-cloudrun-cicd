import os
from flask import Flask
import mysql.connector


app = Flask(__name__)


def get_db_connection():
    """
    Create a MySQL connection with a timeout.
    Timeout is critical for Cloud Run to avoid hanging requests.
    """
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
        connection_timeout=5,  # Prevent infinite hang
    )


@app.route("/")
def show_users():
    """
    Root endpoint:
    - CI mode: DB not configured → safe response
    - Runtime mode: fetch data from MySQL
    """

    # CI-safe behavior (no DB in GitHub Actions)
    if not os.environ.get("DB_HOST"):
        return "CI mode: DB not configured", 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, email FROM users")
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

    except Exception as e:
        # Always return a response (never hang)
        return f"Database error: {str(e)}", 500

    # Build HTML response
    output = "<h1>Users from MySQL</h1><ul>"
    for row in rows:
        output += f"<li>{row[0]} - {row[1]} ({row[2]})</li>"
    output += "</ul>"

    return output, 200


if __name__ == "__main__":
    # Cloud Run requires listening on PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
