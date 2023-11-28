from app import app, items_db
from flask import request, jsonify
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required
from utils import serialize_object_ids

@app.route("/find", methods=["PUT"])
@jwt_required()  # Requires a valid JWT token
def find():
    try:
        # Pobierz parametr "text" z ciała zapytania PUT
        text = request.get_json().get("text", "")
        
        # Użyj regexa do wyszukiwania na podstawie przekazanego tekstu
        items = items_db.find({"name": {"$regex": f".*{text}.*", "$options": "i"}})
        
        if items:
            return jsonify(
                {"items": serialize_object_ids(items), "message": "Success", "code": 200}
            )
        else:
            return jsonify({"message": "No items found", "code": 404})
    except Exception as e:
        return jsonify({"message": str(e), "code": 500})
