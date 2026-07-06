from flask import Blueprint, request, jsonify, session
from backend import db
from backend.models.farmer_model import Farmer

auth = Blueprint("auth", __name__)


# =====================================
# REGISTER
# POST: /api/auth/register
# =====================================
@auth.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data received."}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    farm_name = data.get("farm_name")

    if not username or not email or not password:
        return jsonify({
            "status": "error",
            "message": "Username, email, and password are required."
        }), 400

    if Farmer.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "Username already taken."}), 400

    if Farmer.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Email already registered."}), 400

    new_farmer = Farmer(
        username=username,
        email=email,
        farm_name=farm_name
    )
    new_farmer.set_password(password)

    db.session.add(new_farmer)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": "Account created successfully.",
        "farmer": new_farmer.to_dict()
    }), 201


# =====================================
# LOGIN
# POST: /api/auth/login
# Accepts EITHER username or email in "identifier"
# =====================================
@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "message": "No data received."}), 400

    identifier = data.get("identifier")
    password = data.get("password")

    if not identifier or not password:
        return jsonify({
            "status": "error",
            "message": "Username/email and password are required."
        }), 400

    # Check username first, then email
    farmer = Farmer.query.filter_by(username=identifier).first()
    if not farmer:
        farmer = Farmer.query.filter_by(email=identifier).first()

    if not farmer or not farmer.check_password(password):
        return jsonify({"status": "error", "message": "Invalid credentials."}), 401

    # Store logged-in farmer's ID in the session
    session["farmer_id"] = farmer.id

    return jsonify({
        "status": "success",
        "message": "Login successful.",
        "farmer": farmer.to_dict()
    })


# =====================================
# LOGOUT
# POST: /api/auth/logout
# =====================================
@auth.route("/logout", methods=["POST"])
def logout():
    session.pop("farmer_id", None)
    return jsonify({"status": "success", "message": "Logged out."})


# =====================================
# GET CURRENT LOGGED-IN FARMER
# GET: /api/auth/me
# =====================================
@auth.route("/me", methods=["GET"])
def me():
    farmer_id = session.get("farmer_id")

    if not farmer_id:
        return jsonify({"status": "error", "message": "Not logged in."}), 401

    farmer = Farmer.query.get(farmer_id)
    if not farmer:
        return jsonify({"status": "error", "message": "Farmer not found."}), 404

    return jsonify({"status": "success", "farmer": farmer.to_dict()})