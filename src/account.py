from io import BytesIO
from app import app, users_db, fs
from flask import request, jsonify, send_file
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, current_user
from utils import serialize_object_ids

@app.route('/user_image/<image_id>', methods=['GET'])
def user_image(image_id):
    file = fs.get(ObjectId(image_id))
    return send_file(BytesIO(file.read()), mimetype='image/jpeg')

@app.route("/change_email", methods=["POST"])
@jwt_required()
def change_email():
    if "newEmail" not in request.json:
        return jsonify({"message": "Missing newEmail field", "code": 400})
    
    newEmail = request.json.get("newEmail")

    users_db.update_one(
        {"nickname": current_user["nickname"]}, {"$set": {"email": newEmail}}
    )
    return jsonify({"message": "Success", "code": 200})


@app.route("/change_password", methods=["POST"])
@jwt_required()
def change_password():
    if "newPassword" not in request.json:
        return jsonify({"message": "Missing newPassword field", "code": 400})
    
    newPassword = request.json.get("newPassword")
    if len(newPassword.strip()) == 0:
        return jsonify(
            {"message": "Password has no non-whitespace symbols", "code": 418}
        )

    users_db.update_one(
        {"nickname": current_user["nickname"]},
        {"$set": {"password": newPassword}},
    )
    return jsonify({"message": "Success", "code": 200})

# Define an endpoint for retrieving is user is owner of item
@app.route("/is_owner/<item_id>", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def is_owner(item_id):
    user = current_user

    if user:
        user_items = user.get("items", [])

        for item in user_items:
            if str(item["_id"]) == item_id:
                return jsonify({"isOwner": True})

        return jsonify({"isOwner": False})
    else:
        return jsonify({"message": "User not found", "code": 404})
    
# Define an endpoint for updating user data
@app.route("/update_user", methods=["POST"])
@jwt_required()
def update_user():
    user = current_user

    if user:
        user_data = request.form.to_dict()

        required_fields = ["nickname", "fullName", "email", "phone", "address", "country"]

        if not all(field in user_data for field in required_fields):
            return jsonify(
                {
                    "message": "Missing required fields",
                    "code": 400,
                    "required_fields": required_fields,
                }
            )

        if "photo" in request.files:
            user_image = request.files["photo"]
            image_id = fs.put(user_image.read(), filename=user_image.filename)
            user_data["photoUrl"] = f"https://cosmicretailer.onrender.com/user_image/{image_id}"
        else:
            if "photoUrl" not in user:
                user_data["photoUrl"] = None
            else: 
                user_data["photoUrl"] = user["photoUrl"]

        update_fields = {
            "email": user_data["email"],
            "phone": user_data["phone"],
            "address": user_data["address"],
            "country": user_data["country"],
            "fullName": user_data["fullName"],
            "photoUrl": user_data["photoUrl"]
        }

        update_query = {
            "$set": update_fields
        }

        filter_query = {
            "nickname": user["nickname"]
        }

        users_db.update_one(filter_query, update_query)

        return jsonify({"message": "Success", "code": 200})
    else:
        return jsonify({"message": "User not found", "code": 404})
    
# Define an endpoint for retrieving user data
@app.route("/get_user", methods=["GET"])
@jwt_required()
def get_user():
    user = current_user

    if user:
        items = user.get("items", [])
        history = user.get("history", [])
        ratings = user.get("ratings", [])
        favorites = user.get("favorites", [])
        bucket = user.get("bucket", [])

        user_data = {
            "nickname": user["nickname"],
            "fullName": user.get("fullName", ""),
            "email": user["email"],
            "phone": user.get("phone", ""),
            "address": user.get("address", {}),
            "country": user.get("country", ""),
            "photoUrl": user.get("photoUrl", None),
            "rating_avg": user.get("rating_avg", 0),
            "items": serialize_object_ids(items),
            "history": serialize_object_ids(history),
            "ratings": serialize_object_ids(ratings),
            "favorites": serialize_object_ids(favorites),
            "bucket": serialize_object_ids(bucket),
            "walletAddress": user.get("walletAddress", '')
        }

        return jsonify({"user": user_data, "code": 200})
    else:
        return jsonify({"message": "User not found", "code": 404})
    
# Define an endpoint for retrieving user data by id
@app.route("/get_user_by_id/<user_id>", methods=["GET"])
@jwt_required()
def get_user_by_id2(user_id):
    user = users_db.find_one({"_id": ObjectId(user_id)})

    if user:
        items = user.get("items", [])
        history = user.get("history", [])
        ratings = user.get("ratings", [])
        favorites = user.get("favorites", [])
        bucket = user.get("bucket", [])

        user_data = {
            "nickname": user["nickname"],
            "fullName": user.get("fullName", ""),
            "email": user["email"],
            "phone": user.get("phone", ""),
            "address": user.get("address", {}),
            "country": user.get("country", ""),
            "photoUrl": user.get("photoUrl", None),
            "rating_avg": user.get("rating_avg", 0),
            "items": serialize_object_ids(items),
            "history": serialize_object_ids(history),
            "ratings": serialize_object_ids(ratings),
            "favorites": serialize_object_ids(favorites),
            "bucket": serialize_object_ids(bucket),
            "walletAddress": user.get("walletAddress", '')
        }

        return jsonify({"user": user_data, "code": 200})
    else:
        return jsonify({"message": "User not found", "code": 404})
    
# Define an endpoint for retrieving user data
@app.route("/get_user_wallet/<user_id>", methods=["GET"])
@jwt_required()
def get_user_by_id(user_id):
    user = users_db.find_one({"_id": ObjectId(user_id)})

    if user:
        wallet = user.get("walletAddress", '')
        if wallet == '':
            return jsonify({"message": "User has no wallet", "code": 404}), 404

        return jsonify({"walletAddress": wallet, "code": 200}), 200
    else:
        return jsonify({"message": "User not found", "code": 404}), 404

@app.route("/set_wallet_address", methods=["POST"])
def send_wallet_address():
    nickname = request.json.get("nickname")
    wallet_address = request.json.get("walletAddress")

    users_db.update_one(
        {"nickname": nickname}, {"$set": {"walletAddress": wallet_address}}
    )
    return jsonify({"message": "Success", "code": 200})

@app.route("/update_wallet_address", methods=["POST"])
@jwt_required()
def update_wallet_address():
    wallet_address = request.json.get("walletAddress")

    users_db.update_one(
        {"nickname": current_user["nickname"]}, {"$set": {"walletAddress": wallet_address}}
    )
    return jsonify({"message": "Success", "code": 200})

@app.route("/get_history", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def get_history():
    user = current_user
    if user:
        history = user.get("history", [])
        return jsonify({
            "history": serialize_object_ids(history),
            "message": "Success",
            "code": 200
        })

    return jsonify({"message": "User not found", "code": 404})

@app.route("/get_user_items", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def get_user_items():
    user = current_user
    if user:
        items = user.get("items", [])
        return jsonify({
            "items": serialize_object_ids(items),
            "message": "Success",
            "code": 200
        })

    return jsonify({"message": "User not found", "code": 404})