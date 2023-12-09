from datetime import datetime, timedelta
from app import app, users_db, jwt
from flask import request, jsonify
from bson.objectid import ObjectId
from re import fullmatch
from jwt import encode
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import jwt_required


@app.route("/login", methods=["POST"])
def login():
    required_fields = ["nickname", "password"]

    if not all(field in request.json for field in required_fields):
        return jsonify(
            {
                "message": "Missing required fields",
                "code": 400,
                "required_fields": required_fields,
            }
        )

    name = request.json.get("nickname")
    password = request.json.get("password")
    x = users_db.find_one({"nickname": name})

    if x and pbkdf2_sha256.verify(password, x["password"]):
        # Generate a JWT token
        token = encode(
            {
                "user_id": str(x["_id"]),
                "sub": str(x["_id"]),
                "exp": datetime.utcnow() + timedelta(days=1),
            },
            app.secret_key,
            algorithm="HS256",
        )

        return jsonify(
            {"access_token": token, "message": "Success", "code": 200}
        )

    return jsonify({"message": "Incorrect password or login", "code": 418})


@app.route("/register", methods=["POST"])
def register():
    required_fields = ["email", "nickname", "password"]

    if not all(field in request.json for field in required_fields):
        return jsonify(
            {
                "message": "Missing required fields",
                "code": 400,
                "required_fields": required_fields,
            }
        )

    email = request.json.get("email")
    name = request.json.get("nickname")
    password = request.json.get("password")

    if users_db.find_one({"nickname": name}) is not None:
        return jsonify(
            {"message": "This nickname is already in use", "code": 418}
        )
    if not fullmatch(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", email
    ):
        return jsonify(
            {"message": "This is not a proper email address", "code": 418}
        )
    if users_db.find_one({"email": email}) is not None:
        return jsonify({"message": "This email is already in use", "code": 418})

    # Hash the password before storing it
    hashed_password = pbkdf2_sha256.hash(password)

    users_db.insert_one(
        {
            "email": email,
            "nickname": name,
            "password": hashed_password,
            "rating_avg": 0,
            "items": [],
            "history": [],
            "address": "",
            "ratings": [],
            "favorites": [],
            "bucket": [],
            "photoUrl": "",
            "phone": "",
            "fullName": "",
            "country": "",
            "walletAddress": "",
        }
    )

    x = users_db.find_one({"nickname": name})

    token = encode(
        {
            "user_id": str(x["_id"]),
            "sub": str(x["_id"]),
            "exp": datetime.utcnow() + timedelta(days=1),
        },
        app.secret_key,
        algorithm="HS256",
    )
    return jsonify({"access_token": token, "message": "Success", "code": 200})


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jsonify({"message": "Success", "code": 200})


# Define the user lookup callback
@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    user_id = jwt_data["sub"]  # Assuming "sub" contains the user ID
    user = users_db.find_one({"_id": ObjectId(user_id)})
    return user
