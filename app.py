from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    from services.users import get_users
    return jsonify(get_users())


@app.route("/add", methods=["POST"])
def add_user():
    from services.users import create_user

    data = request.json
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return {"error": "name and email required"}, 400

    create_user(name, email)
    return {"status": "user created"}, 201
