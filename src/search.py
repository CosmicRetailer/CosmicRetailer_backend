import json
from app import app, items_db
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from utils import serialize_object_ids

@app.route("/find/<text>", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def find(text):
    items = items_db.find({"name": {"$regex": f".*{text}.*", "$options": "i"}})
    if items:
        return jsonify(
            {"items":  items, "message": "Success", "code": 200}
        )
    else:
        return jsonify({"message": "No items found", "code": 404})