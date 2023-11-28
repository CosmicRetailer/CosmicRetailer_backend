import json
from app import app, items_db
from flask import request, jsonify
from flask_jwt_extended import jwt_required
from utils import serialize_object_ids

@app.route("/find", methods=["GET"])
@jwt_required()  # Requires a valid JWT token
def search():
    
    return jsonify({"message": "No items found", "code": 404})
