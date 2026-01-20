import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify

# -------------------------
# LOGGING CONFIG (CRITICAL)
# -------------------------
# This makes INFO logs visible in Cloud Run Logs
logging.basicConfig(level=logging.INFO)

# -------------------------
# FLASK APP
# -------------------------
app = Flask(__name__)


# -------------------------
# FRONTEND ROUTE
# -------------------------
@app.route("/", methods=["GET"])
def index():
    from services.users import get_users

    users = get_users()
    return render_template("index.html", users=users)


# -------------------------
# FORM SUBMISSION
# -------------------------
@app.route("/add", methods=["POST"])
def add_user():
    from services.users import create_user

    name = request.form.get("name")
    email = request.form.get("email")

    if not name or not email:
        return "Name and Email required", 400

    create_user(name, email)
    return redirect(url_for("index"))


# -------------------------
# API ENDPOINT (OPTIONAL)
# -------------------------
@app.route("/api/users", methods=["GET"])
def users_api():
    from services.users import get_users

    return jsonify(get_users())


# -------------------------
# LOCAL RUN (NOT USED IN CLOUD RUN)
# -------------------------
if __name__ == "__main__":
    import os

    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
