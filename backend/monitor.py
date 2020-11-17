import time
import requests

from backend.models import Contact

class MonitorService():
    def __init__(self, route, app, onion_session):
        self.route = route
        self.app = app
        self.service_running = False
        self.onion_session = onion_session
        # self.api_port = kwargs['port']


    def monitor_contacts(self):
        contacts = Contact.query.filter(Contact.address != self.route).all()
        for contact in contacts:
            try:
                self.onion_session.get(
                    f'http://{contact.address}/healthz/'
                )
                # Set contact to online status
                contact.online = True
                contact.save()

                # TODO: send queued messages
            except:
                # Set contact to offline status
                contact.online = False
                contact.save()

    def start(self):
        self.service_running = True
        while self.service_running:
            with self.app.app_context():
                self.monitor_contacts()
                time.sleep(10)

    def stop(self):
        self.service_running = False