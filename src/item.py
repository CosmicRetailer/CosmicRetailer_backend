from app import app, users_db, items_db
from flask import request, jsonify
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, current_user  # Import JWT

# Define an endpoint for retrieving a specific item by item_id
@app.route("/get_item/<item_id>", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def get_item(item_id):
    item_id = ObjectId(item_id)  # Convert the item_id to ObjectId

    items = items_db.find_one({"_id": item_id})
    if items:
        return jsonify({"item": items, "message": "Success", "code": 200})

    return jsonify({"message": "Item not found", "code": 404})


# Define an endpoint for adding a new item
@app.route("/add_item", methods=["POST"])
@jwt_required()  # Requires a valid JWT token
def add_item():
    user = current_user 

    if user:
        item_data = request.json
        item_id = ObjectId()
        item_data['_id'] = item_id

        user_items = user.get("items", [])
        user_items.append(item_data)

        items_db.insert_one(item_data)

        # Update the user's items in the database
        users_db.update_one(
            {"_id": user["_id"]}, {"$set": {"items": user_items}}
        )
        return jsonify({"message": "Item added successfully", "code": 200})
    else:
        return jsonify({"message": "User not found", "code": 404})


# Define an endpoint for deleting an item
@app.route("/delete_item/<item_id>", methods=["DELETE"])
@jwt_required()  # Requires a valid JWT token
def delete_item(item_id):
    user = current_user 

    if user:
        user_items = user.get("items", [])
        item_id = ObjectId(item_id)

        if item_id in [item.get("_id") for item in user_items]:
            user_items = [
                item for item in user_items if item.get("_id") != item_id
            ]

            # Update the user's items in the database
            users_db.update_one(
                {"_id": user["_id"]}, {"$set": {"items": user_items}}
            )

            # Delete the item from the items database
            items_db.delete_one({"_id": item_id})

            return jsonify(
                {"message": "Item deleted successfully", "code": 200}
            )
        else:
            return jsonify({"message": "Item not found", "code": 404})
    else:
        return jsonify({"message": "User not found", "code": 404})


# Define an endpoint for updating an item
@app.route("/update_item/<item_id>", methods=["PUT"])
@jwt_required()  # Requires a valid JWT token
def update_item(item_id):
    user = current_user 

    if user:
        user_items = user.get("items", [])
        item_id = ObjectId(item_id)

        # Find the index of the item to update
        item_index = None
        for i, item in enumerate(user_items):
            if item.get("_id") == item_id:
                item_index = i
                break

        if item_index is not None:
            new_item_data = (
                request.json
            )  # Assuming the updated item data is sent as JSON
            user_items[item_index].update(new_item_data)

            # Update the user's items in the database
            users_db.update_one(
                {"_id": user["_id"]}, {"$set": {"items": user_items}}
            )

            # Update the item in the items database
            items_db.update_one(
                {"_id": item_id}, {"$set": new_item_data}
            )
            return jsonify(
                {"message": "Item updated successfully", "code": 200}
            )
        else:
            return jsonify({"message": "Item not found", "code": 404})
    else:
        return jsonify({"message": "User not found", "code": 404})