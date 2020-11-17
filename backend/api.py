import requests
from requests.exceptions import ConnectionError
import logging
import json
import os
import time
import threading

from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_restx import Api, marshal

from backend.db import db
from backend.api_namespace import api as namespace_api, message_model, contact_model, room_model
from backend.models import Message, Contact, Room
from backend.monitor import MonitorService

logging.basicConfig(
    format='%(asctime)s [%(levelname)-8s] (%(filename)-10s:%(lineno)3d) (%(name)s) %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

json_headers = {
    'Content-Type': 'application/json'
}

## Set proper proxies for .onion hostnames (Tor Network)

def create_app(address, **kwargs):
    app = Flask(__name__)
    
    db_path = os.path.expanduser(kwargs['data_folder'] + '/calsotchat.sqlite')
    logging.info(f'DB file -> sqlite:///{db_path}')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    cors = CORS(app, resources={r"/api*": {"origins": "*"}})

    db.init_app(app)

    with app.app_context():
        db.create_all()
        
        # Check if current user is created in db, otherwise create it
        myself = Contact.query.filter_by(address=address).first()
        if not myself:
            myself = Contact(
                nickname="",
                address=address,
                online=True
            )
            myself.save()
            logging.info("Local user created")

        return app

    # app.config['SECRET_KEY'] = '7110c8ae51a4b5af97be6534caef90e4bb9bdcb3380af008f90b23a5d1616bf319bc298105da20fe'

class MainApi():
    """
    API server powered by Flask
    """

    def __init__(self, origin, **kwargs):
        self.onion_session = requests.session()
        self.onion_session.proxies = {
            'http':  f'socks5h://127.0.0.1:{kwargs["onion_socks_port"]}', 
            'https': f'socks5h://127.0.0.1:{kwargs["onion_socks_port"]}'
        }

        self.running = False
        self.port = None
        self.app = create_app(origin, **kwargs)
        self.api = Api(
            self.app, 
            title='CalsotChat API',
            description='',
            doc=False
        )
        self.api.add_namespace(namespace_api, path='/api')

        self.socketio = SocketIO(cors_allowed_origins="*")
        self.socketio.init_app(self.app)
        self.origin = origin

        self._define_internal_routes()

        logging.debug("MainApi class init finished")

    def _define_internal_routes(self):
        @self.app.before_request
        def before_func():
            # TODO
            # logging.info("Test")
            pass

        @self.app.route("/shutdown/")
        def shutdown():
            self.running = False
            self.socketio.stop()
            return ""
        
        @self.app.route("/healthz/")
        def healthz():
            return {"status":"ok"}
        
        @self.app.route("/api/myself/")
        def myself():
            me = Contact.query.filter_by(address=self.origin).first()
            return marshal(me, contact_model)

        @self.api.expect(message_model, validate=True)
        @self.app.route('/api_internal/new_message/', methods=['POST'])
        def new_message():
            content = self.api.payload
            del content['id']
            del content['sender']
            del content['timestamp']

            sender = Contact.query.filter_by(address=content['sender_address']).first()
            if not sender:
                sender = Contact(
                    nickname=content['sender_nickname'],
                    name=content['sender_nickname'],
                    address=content['sender_address'],
                    online=True
                )
                room = sender.save()

                # Emit new contact event
                self.socketio.emit('newContact', marshal(room, room_model), namespace="/api/internal")
            logging.info(f"Message received from {sender.name}")

            message = Message(**content)
            # message.status = MessageStatus.RECEIVED
            logging.info(message)
            logging.info(content)

            if message.room_hash == self.origin: # Direct message to me -> overwrite the room_hash
                message.room_hash = content['sender_address']

            message.save()

            self.socketio.emit('newMessage', marshal(message, message_model), namespace="/api/internal")
            return {"message": "received"}

        @self.socketio.on('send-message', namespace="/api/internal")
        def handleMessage(content):
            me = Contact.query.filter_by(address=self.origin).first()

            message = Message(
                sender_address=me.address,
                sender_nickname=me.nickname,
                room_hash=content['room_hash'],
                msg=content['msg'],
                # status=MessageStatus.QUEUED,

            )
            message.save()

            receivers = Room.query.filter_by(hash=content['room_hash']).first().members
            some_failed = False

            message_json = marshal(message, message_model)
            for receiver in receivers: # TODO: review and make it more asyncronous
                if receiver.address != self.origin:
                    try:
                        self.onion_session.post(
                            f'http://{receiver.address}/api_internal/new_message/', 
                            data=json.dumps(message_json),
                            headers=json_headers
                        )
                        logging.info(f"Message {message.id} sent to {receiver.name}")
                    except ConnectionError:
                        some_failed = True
                        logging.warning(f"Message can not be sent to {receiver.name}")
                    except Exception as e:
                        some_failed = True
                        logging.exception(e)
            
            # if not some_failed:
            #     message.status = MessageStatus.DISPATCHED
            #     message.save()

    def start(self, port=5000, dev=False):
        """
        Start the Flask web server
        """

        # Start monitor service
        self.monitor = MonitorService(self.origin, self.app, self.onion_session)
        thread = threading.Thread(target=self.monitor.start)
        thread.daemon = True
        thread.start()

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
            self.monitor.stop()
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

    api = MainApi('gxf3xsmy6trcaugd5pvfpr652qxnzizx4zxf5smcwtczobters37awad.onion:8080')

    api.start(dev=True)