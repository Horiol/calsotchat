import requests
from requests.exceptions import ConnectionError
import logging
import json
import time

from flask import Flask, request, jsonify
from flask.json import dumps
from flask_cors import CORS
from flask_socketio import SocketIO
from db import db
from models import Message, Contact, Room, MessageStatus
# from backend.models import Message, Contact, Room


logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)-8s] (%(threadName)-10s) (%(filename)-10s:%(lineno)3d) %(message)s',
)

def create_app(address):
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calsotchat.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)

    with app.app_context():
        db.create_all()
        
        # Check if current user is created in db, otherwise create it
        myself = Contact.query.filter_by(address=address).first()
        if not myself:
            myself = Contact(
                name="Current User",
                address=address,
                online=True
            )
            myself.save()
            logging.info("'Current User' created")

        return app

    # app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'


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
        self.app = create_app(origin)
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
        
        @self.app.route("/healthz/")
        def healthz():
            return {"status":"ok"}

        @self.app.route('/api/new_message', methods=['POST'])
        def new_message():
            content = request.json

            sender = Contact.query.filter_by(address=content['sender_address']).first()
            if not sender:
                sender = Contact(
                    name="Unknown",
                    address=content['sender_address'],
                    online=True
                )
                sender.save()
            logging.info(f"Message received from {sender.name}")

            message = Message()
            message.from_json(content)
            message.save()

            self.socketio.emit('newMessage', message.to_json(), namespace="/internal")
            return {"message": "received"}
        
        @self.app.route('/api/messages', methods=['GET'])
        def get_message():
            messages = Message.query.all()

            return jsonify(messages)

        @self.socketio.on('connect', namespace='/internal')
        @self.socketio.on('update-status', namespace='/internal')
        def updateStatus():
            status = {
                "own_route": self.origin
            }
            self.socketio.emit('statusResponse', status, namespace="/internal")

            # Emit a list of all contacts
            contacts = Contact.query.filter(Contact.address != self.origin).all()
            self.socketio.emit('contactList', json.loads(dumps(contacts)), namespace="/internal")

        @self.socketio.on('send-message', namespace='/internal')
        def handleMessage(content):
            message = Message(
                sender_addres=self.origin,
                room_id=content['room_id'],
                msg=content['msg'],
                status=MessageStatus.QUEUED
            )
            message.save()

            receivers = Room.query.get(content['room_id']).members
            for receiver in receivers: # TODO: review and make it more asyncronous
                onion_session.post(
                    f'http://{receiver["address"]}/api/new_message', 
                    data=json.dumps(message.to_json()),
                    headers=json_headers
                )
                logging.info(f"Message {message.id} sent to {receiver.name}")
            
            message.status = MessageStatus.DISPATCHED
            message.save()

    def start(self, port=5000, dev=False):
        """
        Start the Flask web server
        """
        if not self.running:
            self.port = port
            self.running = True
            if dev:
                self.socketio.run(
                    self.app, 
                    host="127.0.0.1", 
                    port=port,
                    debug=True, 
                    use_reloader=True,
                )
            else:
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

if __name__ == "__main__":
    """
    code only for development
    """

    api = Api('gxf3xsmy6trcaugd5pvfpr652qxnzizx4zxf5smcwtczobters37awad.onion:8080')

    api.start(dev=True)