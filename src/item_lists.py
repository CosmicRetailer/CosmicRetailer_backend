import json
from app import app, users_db, items_db
from utils import convert_to_json_serializable
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from bson import ObjectId


# def get_paginated_items(item_list, page, per_page):
#     start = (page - 1) * per_page
#     end = start + per_page
#     return item_list[start:end]


# Define an endpoint for displaying a specific user's items
@app.route("/user_items/<user_id>", methods=["GET"])
@jwt_required()
def get_specific_user_items(user_id):
    # page = int(request.args.get("page", 1))
    # per_page = int(request.args.get("per_page", 10))

    # user = users_db.find_one({"_id": ObjectId(user_id)})

    # if user:
    #     user_items = user.get("items", [])
    #     paginated_items = get_paginated_items(user_items, page, per_page)
    #     paginated_items_json_serializable = json.loads(json.dumps(paginated_items, default=convert_to_json_serializable))

    #     return jsonify(
    #         {"items": paginated_items_json_serializable, "message": "Success", "code": 200}
    #     )
    # else:
    #     return jsonify({"message": "User not found", "code": 404})

    user = users_db.find_one({"_id": ObjectId(user_id)})

    if user:
        user_items = user.get("items", [])
        user_items_serializable = json.loads(json.dumps(list(user_items), default=convert_to_json_serializable))

        return jsonify(
            {"items": user_items_serializable, "message": "Success", "code": 200}
        )
    else:
        return jsonify({"message": "User not found", "code": 404})


# Define an endpoint to retrieve all items for all users
@app.route("/all_items", methods=["GET"])
@jwt_required()
def get_all_items():
    # page = int(request.args.get("page", 1))
    # per_page = int(request.args.get("per_page", 10))

    # skip = (page - 1) * per_page

    # paginated_items_cursor = items_db.find().skip(skip).limit(per_page)
    # paginated_items = list(paginated_items_cursor)

    # paginated_items_json_serializable = json.loads(json.dumps(paginated_items, default=convert_to_json_serializable))

    # return jsonify(
    #     {"items": paginated_items_json_serializable, "message": "Success", "code": 200}
    # )

    items = items_db.find()
    items_serializable = json.loads(json.dumps(list(items), default=convert_to_json_serializable))

    if items:
        return jsonify(
            {"items": items_serializable, "message": "Success", "code": 200}
        )

    return jsonify({"message": "Items not found", "code": 404})

#Define an endpoint to retrive active user items from history
@app.route("/get_history_items", methods=["GET"])
@jwt_required()
def get_history_items():
    user_id = request.args.get("user_id")
    user = users_db.find_one({"_id": ObjectId(user_id)})
    if user:
        user_items = user.get("history", [])
        user_items_serializable = json.loads(json.dumps(list(user_items), default=convert_to_json_serializable))
        return jsonify(
            {"items": user_items_serializable, "message": "Success", "code": 200}
        )
    else:
        return jsonify({"message": "User not found", "code": 404})