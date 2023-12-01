from bson import ObjectId
from app import app, users_db, ratings_db
from flask import request, jsonify
from flask_jwt_extended import jwt_required, current_user

# Define an endpoint for adding a rating and comment
@app.route("/add_rating", methods=["POST"])
@jwt_required()
def add_rating():
    seller_name = request.json.get("sellerName")
    comment = request.json.get("comment")
    rating = request.json.get("rating")

    # Find the seller's user document by name
    seller = users_db.find_one({"nickname": seller_name})

    if seller:
        rating_id = ObjectId()

        # Add the rating and comment to the seller's ratings array
        seller_ratings = seller.get("ratings", [])
        seller_ratings.append(
            {
                "_id": rating_id,
                "user": current_user["nickname"],
                "rating": rating,
                "comment": comment,
            }
        )

        # Update the seller's ratings and points
        seller["ratings"] = seller_ratings
        seller_points = sum(
            rating["rating"] for rating in seller_ratings
        ) / len(seller_ratings)
        seller["rating_avg"] = seller_points

        # Update the seller's user document in the database
        users_db.update_one(
            {"_id": seller["_id"]},
            {"$set": {"ratings": seller_ratings, "rating_avg": seller_points}},
        )

        # Add the rating to the ratings collection
        ratings_db.insert_one(
            {
                "_id": rating_id,
                "user": seller["nickname"],
                "rating": rating,
                "comment": comment,
            }
        )

        return jsonify({"message": "Rating added successfully", "code": 200})
    else:
        return jsonify({"message": "Seller not found", "code": 404})
