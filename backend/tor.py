import time
import shlex

from stem.control import Controller

class Tor():
    """
    Class created to group all the logic and workflow of onion hidden services
    using stem library
    """

    def __init__(self):
        # self.tor_proc = None # The tor process
        self.controller = None # The Tor controller
        self.service = None # Onion Service
        self.tor_control_port = 9051 # Tor control port

    def start_service(self, port=5000):
        """Start Onion Hidden Services

        Args:
            port (int): local port that will be listenint the service

        Returns:
            str: onion address assigned to this service
        """
        if self.service is None:
            self.controller = Controller.from_port(port=self.tor_control_port)
            self.controller.authenticate()

            # Create Onion Hidden Service
            self.service = self.controller.create_ephemeral_hidden_service(
                {80: port}, 
                await_publication = True
            )
            
        # return onion route
        return self.service.service_id + ".onion"

    def stop_service(self):
        if self.service is not None:
            self.controller.remove_ephemeral_hidden_service(self.service.service_id)
            self.service = None