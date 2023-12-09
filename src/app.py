import os
from flask import Flask
from flask_cors import CORS
import json
import pymongo
from flask_jwt_extended import JWTManager
from gridfs import GridFS
from web3 import Web3

app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_REQUIRED_CLAIMS"] = ["sub", "exp"]

jwt = JWTManager(app)

CORS(app, supports_credentials=True)
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = (("http://localhost:5173", "http://localhost:5000"),)

with open("config.json") as config_file:
    config_data = json.load(config_file)

app.config.update(config_data)

web3 = Web3(Web3.HTTPProvider(app.config["INFURA_API_URL"]))  

mongo_client = pymongo.MongoClient(app.config["MONGO_API"])
fs = GridFS(mongo_client["data"])

app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

users_db = mongo_client["data"]["users"]
items_db = mongo_client["data"]["items"]
ratings_db = mongo_client["data"]["ratings"]
notifications_db = mongo_client["data"]["notifications"]

# rationale for that kind of imports:
# https://stackoverflow.com/questions/11994325/how-to-divide-flask-app-into-multiple-py-files
import log_in as log_in
import account as account
import item as item
import item_lists as item_lists
import favorite as favorite
import bucket as bucket
import search as search
import rating as rating
import wallet as wallet
import notification as notification
