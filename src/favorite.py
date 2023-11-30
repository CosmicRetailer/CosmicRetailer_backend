from app import app, fs, users_db, items_db
from flask import jsonify, request
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, current_user  # Import JWT
import requests
from utils import serialize_object_ids,convert_to_json_serializable
import json

# Define an endpoint for toggling favorite item by item_id
@app.route("/toggle_favorite/<item_id>", methods=["PUT"])
@jwt_required()  # Requires a valid JWT token
def toggle_favorite(item_id):
    user = current_user

    if user:
        headers = {"Authorization": f"{request.headers.get('Authorization')}"}

        # Check if the current user is the owner of the item
        is_owner_response = requests.get(f"https://cosmicretailer.onrender.com/is_owner/{item_id}", headers=headers)
        is_owner_data = is_owner_response.json()

        if is_owner_data['isOwner']:
            return jsonify({"message": "You can't favorite your own item", "code": 400})

        favorite_items = user.get("favorites", [])

        for item in favorite_items.copy():  # Use copy() to iterate over a copy
            if item["_id"] == item_id:
                favorite_items.remove(item)
                users_db.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"favorites": favorite_items}},
                )
                return jsonify({"message": "Success", "code": 200})
        
        favorite_items.append({"_id": item_id})
        users_db.update_one(
            {"_id": user["_id"]},
            {"$set": {"favorites": favorite_items}},
        )

        return jsonify({"message": "Success", "code": 200})
    else:
        return jsonify({"message": "User not found", "code": 404})
    
# Define an endpoint for checking if an item is favorite
@app.route("/is_favorite/<item_id>", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def is_favorite(item_id):
    user = current_user

    if user:
        favorite_items = user.get("favorites", [])

        for item in favorite_items:
            if item["_id"] == item_id:
                return jsonify({"isFavorite": True})

        return jsonify({"isFavorite": False})
    else:
        return jsonify({"message": "User not found", "code": 404})

# Define an endpoint for getting all favorite items
@app.route("/get_favorites", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def get_favorites():
    user = current_user

    if user:
        favorite_items = user.get("favorites", [])
        favorites = []

        for item_id in favorite_items.copy():  # Iterate over item IDs
            item = ObjectId(item_id)
            item_doc = items_db.find_one({"_id": item})  # Use ObjectId
            if item_doc:
                favorites.append(item_doc)
            else: 
                favorite_items.remove(item_id)  # Remove item ID
                users_db.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"favorites": favorite_items}},
                )

        # Serialize items to JSON
        items_serializable = json.loads(json.dumps(favorites, default=serialize_object_ids))
        
        return jsonify({"favorites": items_serializable, "message": "Success", "code": 200})
    else:
        return jsonify({"message": "User not found", "code": 404})