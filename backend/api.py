import requests
from requests.exceptions import ConnectionError
import logging

from flask import Flask, request
from backend.socket_logic import socketio
from backend.chat import chat_bp

app = Flask(__name__)
app.register_blueprint(chat_bp)

class Api():
    """
    API server powered by Flask
    """

    def __init__(self):
        self.running = False
        self.port = None
        self.app = app
        self.socketio = socketio
        self.socketio.init_app(self.app)

        self._define_internal_routes()

    def _define_internal_routes(self):
        @self.app.route("/shutdown/")
        def shutdown():
            self.running = False
            self.socketio.stop()
            return ""

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