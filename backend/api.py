import requests
from requests.exceptions import ConnectionError
import logging
import json
import time

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

json_headers = {
    'Content-Type': 'application/json'
}

## Set proper proxies for .onion hostnames (Tor Network)
onion_session = requests.session()
onion_session.proxies = {
    'http':  f'socks5h://127.0.0.1:9050', 
    'https': f'socks5h://127.0.0.1:9050'
}

class Api():
    """
    API server powered by Flask
    """

    def __init__(self, origin):
        self.running = False
        self.port = None
        self.app = app
        self.socketio = SocketIO(cors_allowed_origins="*")
        self.socketio.init_app(self.app)
        self.origin = origin

        self._define_internal_routes()

    def _define_internal_routes(self):
        @self.app.route("/shutdown/")
        def shutdown():
            self.running = False
            self.socketio.stop()
            return ""

        @self.app.route('/api/new_message', methods=['POST'])
        def new_message():
            content = request.json
            print(content['msg'])
            self.socketio.emit('newMessage', content, namespace="/internal")
            return {"message": "received"}

        @self.socketio.on('send-message', namespace='/internal')
        def handleMessage(content):
            data = {
                "msg":content['msg'],
                "origin": self.origin,
                "timestamp": int(time.time())
            }
            onion_session.post(
                f'http://{content["destiny"]}/api/new_message', 
                data=json.dumps(data),
                headers=json_headers
            )

    def start(self, port=5000):
        """
        Start the Flask web server
        """
        if not self.running:
            self.port = port
            self.running = True
            self.socketio.run(
                self.app, 
                host="127.0.0.1", 
                port=port
            )

    def stop(self):
        """
        Stop the Flask web server
        """
        if self.running:
            try:
                requests.get(
                    f"http://127.0.0.1:{self.port}/shutdown/"
                )
            except ConnectionError:
                self.running = False