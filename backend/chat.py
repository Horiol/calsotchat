import requests
import json

from flask import Blueprint, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import session

chat_bp = Blueprint('chat_bp', __name__)

json_headers = {
    'Content-Type': 'application/json'
}

## Set proper proxies for .onion hostnames (Tor Network)
onion_session = requests.session()
onion_session.proxies = {
    'http':  f'socks5h://127.0.0.1:9050', 
    'https': f'socks5h://127.0.0.1:9050'
}

socketio = SocketIO()

@chat_bp.route('/')
def index():
    print("test")
    return "This is an example app"

@chat_bp.route('/new_message', methods=['POST'])
def new_message():
    content = request.json
    print(content['msg'])
    return {"message": "received"}

@chat_bp.route('/send_message', methods=['POST']) # TODO: make it websocket call
def send_message():
    content = request.json
    onion_session.post(f'http://{content["destiny"]}/new_message', data=json.dumps({"msg":content['msg']}), headers=json_headers)
    return {"message": "delivered"}
