import time
import socketio

from backend.models import Contact
from backend.api_namespace import contact_model
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

                    # TODO: send queued messages
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