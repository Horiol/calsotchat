from flask.signals import message_flashed
import requests
from requests.exceptions import ConnectionError
import logging
import json
import os
import time
import threading

from flask import Flask, request, g
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_restx import Api, marshal

from backend.db import db
from backend.api_namespace import api as namespace_api, message_model, contact_model, room_model
from backend.models import Message, Contact, Room, MessageStatus, MessageQueue, Myself
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
        my_contact = Contact.query.filter_by(address=address).first()
        if not my_contact:
            my_contact = Contact(
                nickname="",
                address=address,
                online=True
            )
            my_contact.save()
            logging.info("Local user created")
            myself = Myself(
                address=address,
            )
            myself.save()

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
            g.origin = self.origin
            g.onion_session = self.onion_session
            g.socketio = self.socketio

        @self.app.route("/shutdown/")
        def shutdown():
            self.running = False
            self.socketio.stop()
            return ""

        @self.app.route("/healthz/")
        def healthz():
            return {"status":"ok"}

        @self.api.expect(message_model, validate=True)
        @self.app.route('/api_internal/new_message/', methods=['POST'])
        def new_message():
            content = self.api.payload
            content.pop('id', None)
            content.pop('sender', None)
            content.pop('timestamp', None)
            room = content.pop('room', None)

            sender = Contact.query.filter_by(address=content['sender_address']).first()
            if not sender:
                sender = Contact(
                    nickname=content['sender_nickname'],
                    name=content['sender_nickname'],
                    address=content['sender_address'],
                    online=True
                )
                contact_room = sender.save()

                # Emit new contact event
                self.socketio.emit('newContact', marshal(contact_room, room_model), namespace="/api/internal")
            logging.info(f"Message received from {sender.name}")

            message = Message(**content)
            message.status = MessageStatus.RECEIVED

            if message.room_hash == self.origin: # Direct message to me -> overwrite the room_hash
                message.room_hash = content['sender_address']
                room["hash"] = content['sender_address']
                room["name"] = content['sender_nickname']

            # Check if room exist, create new room if not
            db_room = (
                Room.query.filter_by(hash=content['sender_address']).first()
                if room["private"]
                else Room.query.filter_by(hash=room["hash"]).first()
            )

            if not db_room:
                db_room = marshal(room, room_model)
                db_room.pop("id", None)
                db_members = db_room.pop("members", [])

                new_room = Room(**db_room)
                if not room["private"]:
                    for member in db_members:
                        contact = Contact.query.filter_by(address=member["address"]).first()
                        if not contact:
                            member.pop("name", None)
                            member.pop("id", None)

                            contact = Contact(**member)
                            contact_room = contact.save()
                            self.socketio.emit('newContact', marshal(contact_room, room_model), namespace="/api/internal")

                        new_room.members.append(contact)
                else:
                    new_room.members.append(sender)

                new_room.save()
                self.socketio.emit('newContact', marshal(new_room, room_model), namespace="/api/internal")
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
                status=MessageStatus.QUEUED
            )
            message.save()
            self.socketio.emit('newMessage', marshal(message, message_model), namespace="/api/internal")

            receivers = Room.query.filter_by(hash=content['room_hash']).first().members
            some_failed = False

            message_json = marshal(message, message_model)
            logging.info(message_json)
            logging.info(receivers)
            for receiver in receivers: # TODO: review and make it more asyncronous
                logging.info(receiver.__dict__)
                if receiver.address != self.origin:
                    try:
                        result = self.onion_session.post(
                            f'http://{receiver.address}/api_internal/new_message/', 
                            data=json.dumps(message_json),
                            headers=json_headers
                        )
                        if result.status_code != 200:
                            logging.error(result.content)
                            raise ConnectionError
                        logging.info(f"Message {message.id} sent to {receiver.name}")
                    except ConnectionError:
                        some_failed = True
                        logging.warning(f"Message can not be sent to {receiver.name}")
                        queued_message = MessageQueue(
                            msg_id=message.id,
                            receiver_id=receiver.id,
                            status=MessageStatus.QUEUED
                        )
                        queued_message.save()
                    except Exception as e:
                        some_failed = True
                        logging.exception(e)
            if not some_failed:
                message.update(status=MessageStatus.DISPATCHED)
                self.socketio.emit('updateMessage', marshal(message, message_model), namespace="/api/internal")

        @self.socketio.on('contactUpdate')
        def handleMonitorMessage(content):
            self.socketio.emit('contactUpdate', content, namespace="/api/internal")

        @self.socketio.on('updateMessage')
        def handleMonitorMessage2(content):
            self.socketio.emit('updateMessage', content, namespace="/api/internal")
            

    def start(self, port=5000, dev=False):
        """
        Start the Flask web server
        """

        # Start monitor service
        self.monitor = MonitorService(self.origin, self.app, self.onion_session)
        thread = threading.Thread(target=self.monitor.start, args=(port, ))
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