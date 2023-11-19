from app import app, fs, users_db, items_db
from flask import jsonify, request
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, current_user  # Import JWT
import requests
from utils import serialize_object_ids

# Define an endpoint for toggle favorite item by item_id
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

        for item in favorite_items:
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
        favorite_items_copy = favorite_items.deepcopy()
        favorites = []

        for item in favorite_items_copy:
            item_id = item["_id"]
            item = items_db.find_one({"_id": item_id})
            if item:
                item["_id"] = str(item["_id"])
                favorites.append(item)
            else: 
                favorite_items.remove(item)
                users_db.update_one(
                    {"_id": user["_id"]},
                    {"$set": {"favorites": favorite_items}},
                )

        return jsonify({"favorites": serialize_object_ids(favorites), "message": "Success", "code": 200})
    else:
        return jsonify({"message": "User not found", "code": 404})