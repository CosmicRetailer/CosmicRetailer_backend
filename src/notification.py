from io import BytesIO
from app import app, notifications_db
from utils import convert_to_json_serializable, serialize_object_ids
from flask import jsonify, request
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, current_user  # Import JWT
import json

@app.route("/get_notification", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def get_notifications():
    user_id = ObjectId(current_user["_id"])

    notifications = notifications_db.find_one({"userId": user_id})
    if notifications:
        notifications_serializable = json.loads(
            json.dumps(notifications, default=convert_to_json_serializable)
        )

        # TODO uncomment this
        # delte notification from db
        # notifications_db.delete_many({"userId": user_id})

        return jsonify({
            "notification": notifications_serializable,
            "message": "Success",
            "code": 200
        })
    else:
        return jsonify({
            "message": "No notifications found",
            "code": 400
        })
    
@app.route("/create_notification/<seller_id>", methods=["POST"])
@jwt_required()  # Requires a valid JWT token
def create_notification(seller_id):
    data = request.get_json()
    user_id = ObjectId(current_user["_id"]) # buyer
    # seller id
    seller_id = ObjectId(user_id)

    notification_buyer = {
        "userId": user_id,
        "type": 1, # 0 - seller, 1 - buyer
        "itemId": data["itemId"],
        "itemName": data["itemName"],
    }

    notification_seller = {
        "userId": seller_id,
        "type": 0, # 0 - seller, 1 - buyer
        "itemId": data["itemId"],
        "itemName": data["itemName"],
    }

    notifications_db.insert_one(notification_buyer)
    notifications_db.insert_one(notification_seller)

    return jsonify({
        "message": "Success",
        "code": 200
    })