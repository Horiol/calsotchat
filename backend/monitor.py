import time
import socketio
import json

from backend.models import Contact, Message, MessageStatus
from backend.api_namespace import contact_model, message_model
from flask_restx import marshal

class MonitorService():
    def __init__(self, route, app, onion_session):
        self.route = route
        self.app = app
        self.service_running = False
        self.onion_session = onion_session
        self.socketio = socketio.Client()
        # self.api_port = kwargs['port']

    def _change_contact_status(self, contact, status):
        contact.online = status
        contact.save()
        self.socketio.emit('contactUpdate', marshal(contact, contact_model))

    def _send_queued_messages(self, contact):
        queued_messages = Message.query.filter_by(
            status=MessageStatus.QUEUED,
            room_hash=contact.address
        ).all()

        # Send private queued messages to this contact
        for message in queued_messages:
            message_json = marshal(message, message_model)
            try:
                self.onion_session.post(
                    f'http://{contact.address}/api_internal/new_message/', 
                    data=json.dumps(message_json),
                    headers={'Content-Type': 'application/json'}
                )
                message.update(status=MessageStatus.DISPATCHED)
            except:
                pass

    def monitor_contacts(self):
        contacts = Contact.query.filter(Contact.address != self.route).all()
        for contact in contacts:
            original_status = contact.online
            try:
                self.onion_session.get(
                    f'http://{contact.address}/healthz/'
                )
                if not original_status:
                    # Set contact to online status
                    self._change_contact_status(contact, True)
                    self._send_queued_messages(contact)
            except:
                if original_status:
                    # Set contact to offline status
                    self._change_contact_status(contact, False)

    def start(self, port):
        time.sleep(5)
        self.socketio.connect(f'http://127.0.0.1:{port}')
        
        self.service_running = True
        while self.service_running:
            with self.app.app_context():
                self.monitor_contacts()
                time.sleep(10)

    def stop(self):
        self.service_running = False