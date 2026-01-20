import os
from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)


def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        database=os.environ.get("DB_NAME"),
        connection_timeout=5,
    )


@app.route("/")
def index():
    # CI-safe mode
    if not os.environ.get("DB_HOST"):
        return "CI mode: DB not configured", 200

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        return f"Database error: {str(e)}", 500

    return render_template("index.html", users=users)


@app.route("/add", methods=["POST"])
def add_user():
    name = request.form.get("name")
    email = request.form.get("email")

    if not name or not email:
        return "Name and Email required", 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s)",
            (name, email),
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return f"Database error: {str(e)}", 500

    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
