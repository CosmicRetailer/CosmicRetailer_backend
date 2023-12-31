import json
from app import app, items_db
from utils import convert_to_json_serializable
from flask import jsonify
from flask_jwt_extended import jwt_required

@app.route("/find/<text>", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def find(text):

    items = items_db.find({"name": {"$regex": f".*{text}.*", "$options": "i"}})

    items_serializable = json.loads(json.dumps(list(items), default=convert_to_json_serializable))

    if items:
        return jsonify(
            {"items": items_serializable, "message": "Success", "code": 200}
        )

    return jsonify({"message": "Items not found", "code": 404})

@app.route("/find_tag/<text>", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def find_tag(text):
  
    
    items = items_db.find({"category": {"$regex": f".*{text}.*", "$options": "i"}})
    items_serializable = json.loads(json.dumps(list(items), default=convert_to_json_serializable))

    if items:
        return jsonify(
            {"items": items_serializable, "message": "Success", "code": 200}
        )

    return jsonify({"message": "Items not found", "code": 404})

