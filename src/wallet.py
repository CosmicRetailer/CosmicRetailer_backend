from io import BytesIO
from app import app, fs, users_db, items_db, web3
from utils import convert_to_json_serializable
from flask import request, jsonify, send_file
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required, current_user  # Import JWT
import json
import requests

@app.route('/get_balance', methods=['GET'])
@jwt_required()
def getBalance():
    address = current_user['walletAddress']
    account = web3.to_checksum_address(address)
    balance = web3.eth.get_balance(account)

    return json.dumps({'balance': balance})

@app.route('/buy_item/<item_id>', methods=['POST'])
@jwt_required()
def buyItem(item_id):
    pvk = request.json.get("privateKey")
    if pvk is None:
        return jsonify({'message': 'can\'t buy an item', "code": 400})

    item = items_db.find_one({'_id': ObjectId(item_id)})
    if item is None:
        return jsonify({'message': 'item not found', "code": 404})

    headers = {"Authorization": f"{request.headers.get('Authorization')}"}
    response = requests.get("https://cosmicretailer.onrender.com/get_user_wallet/" + item['userId'], headers=headers)

    from_account = current_user['walletAddress']
    to_account = response.json()['walletAddress']

    account = web3.to_checksum_address(from_account)
    balance = web3.eth.get_balance(account)

    api_request = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USDT"
    response = requests.get(api_request)

    balance_usdt = balance * response.json()['USDT']
    print('balance_usdt & balance & price', balance_usdt, balance, item['price'])

    if balance_usdt < item['price'] + 0.1:
        return jsonify({'message': 'not enough money', "code": 400})
    
    api_request = "https://min-api.cryptocompare.com/data/price?fsym=USDT&tsyms=ETH"
    response = requests.get(api_request)

    balance_eth = item['price'] / response.json()['ETH']
    print('balance_eth', balance_eth)
    print('value', web3.to_wei(balance_eth, 'ether'))
    print('lol balance', balance / response.json()['ETH'])
    
    nonce = web3.eth.get_transaction_count(from_account)  
    tx = {
        'type': '0x2',
        'nonce': nonce,
        'from': from_account,
        'to': to_account,
        'value': web3.to_wei(balance_eth, 'ether'),
        'maxFeePerGas': web3.to_wei('250', 'gwei'),
        'maxPriorityFeePerGas': web3.to_wei('3', 'gwei'),
        'chainId': 11155111
    }
    gas = web3.eth.estimate_gas(tx)
    tx['gas'] = gas
    signed_tx = web3.eth.account.sign_transaction(tx, pvk)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    print("Transaction hash: " + str(web3.to_hex(tx_hash)))

    data = {
        "itemId": item_id,
        "itemName": item['name']
    }
    response = requests.get(
        "https://cosmicretailer.onrender.com/create_notification/" + item['userId'], 
        headers=headers,
        data=data
    )

    # add item to user's history
    # users_db.update_one(
    #     {"_id": ObjectId(current_user['_id'])}, {"$push": {"history": {
    #         "itemId": item_id,
    #         "txHash": str(web3.to_hex(tx_hash)),
    #         "type": "buy"
    #     }}}
    # )
    users_db.find_one_and_update(
        {"_id": ObjectId(current_user['_id'])}, {"$push": {"history": {
            "itemId": item_id,
            "txHash": str(web3.to_hex(tx_hash)),
            "type": "buy",
            "itemName": item['name'],
            "price": item['price'],
            "photoUrl": item['photoUrl'],
        }}}
    )

    hello = users_db.find_one_and_update(
        {"_id": ObjectId(current_user['_id'])}, {"$push": {"history": {
            "itemId": item_id,
            "txHash": str(web3.to_hex(tx_hash)),
            "type": "sell",
            "itemName": item['name'],
            "price": item['price'],
            "photoUrl": item['photoUrl'],
        }}}
    )

    if hello['n'] > 0:
        return jsonify({'message': 'cant buy your own item', "code": 400})
    # users_db.update_one(
    #     {"_id": ObjectId(item['userId'])}, {"$push": {"history": {
    #         "itemId": item_id,
    #         "txHash": str(web3.to_hex(tx_hash)),
    #         "type": "sell"
    #     }}}
    # )

    # delete from favorites
    users_db.update_many(
        {}, {"$pull": {"favorites": item_id}}
    )

    # delte from buckets
    users_db.update_many(
        {}, {"$pull": {"bucket": item_id}}
    )

    # delete from owner's items
    users_db.find_one_and_update(
        {"_id": ObjectId(item['userId'])}, {"$pull": {"items": item_id}}
    )

    # delete item from items_db
    items_db.find_one_and_delete(
        {"_id": ObjectId(item_id)}
    )

    return jsonify({'message': 'success', "hash": str(web3.to_hex(tx_hash)), "code": 200})
