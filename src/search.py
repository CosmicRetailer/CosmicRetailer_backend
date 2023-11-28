import json
from app import app, items_db
from flask import request, jsonify
from bson import ObjectId
from flask_jwt_extended import jwt_required
from utils import serialize_object_ids, convert_to_json_serializable

@app.route("/find/<text>", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def search(text):
    items = items_db.find({"name": {"$regex": f".*{text}.*", "$options": "i"}})
    if items:
        serialized_items = serialize_object_ids(items)
        return jsonify(
            {"items": json.loads(json.dumps(serialized_items, default=convert_to_json_serializable)), "message": "Success", "code": 200}
        )
    else:
        return jsonify({"message": "No items found", "code": 404})
