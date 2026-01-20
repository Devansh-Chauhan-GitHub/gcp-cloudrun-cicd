from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    from services.users import get_users
    users = get_users()
    return render_template("index.html", users=users)


@app.route("/add", methods=["POST"])
def add_user():
    from services.users import create_user

    name = request.form.get("name")
    email = request.form.get("email")

    if not name or not email:
        return "Name and Email required", 400

    create_user(name, email)
    return redirect(url_for("index"))


# Optional: keep API for debugging / future frontend
@app.route("/api/users", methods=["GET"])
def users_api():
    from services.users import get_users
    return jsonify(get_users())
