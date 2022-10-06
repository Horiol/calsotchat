import time
import shlex
import os
import logging

from stem.control import Controller

logging.basicConfig(
    format='%(asctime)s [%(levelname)-8s] (%(filename)-10s:%(lineno)3d) (%(name)s) %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)

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

    def start_service(self, onion_port=80, port=5000, **kwargs):
        """Start Onion Hidden Services

        Args:
            port (int): local port that will be listenint the service

        Returns:
            str: onion address assigned to this service
        """
        if self.service is None:
            self.controller = Controller.from_port(port=self.tor_control_port)
            self.controller.authenticate()

            key_path = os.path.expanduser(kwargs['data_folder'] + '/my_service.key')

            ### If file does not exist create it and use it to create an onion hidden service
            if not os.path.exists(key_path):
                self.service = self.controller.create_ephemeral_hidden_service(
                    {onion_port: port}, 
                    await_publication = True
                )
                logging.info(
                    f"Started a new hidden service with the address of {self.service.service_id}.onion"
                )


                with open(key_path, 'w') as key_file:
                    key_file.write(f'{self.service.private_key_type}:{self.service.private_key}')
                            

            else:
                with open(key_path) as key_file:
                    key_type, key_content = key_file.read().split(':', 1)

                self.service = self.controller.create_ephemeral_hidden_service(
                    {onion_port: port}, 
                    key_type = key_type, 
                    key_content = key_content, 
                    await_publication = True
                )
                logging.info(f"Resumed {self.service.service_id}.onion")


        # return onion route
        route = f"{self.service.service_id}.onion"
        if onion_port != 80:
            route += f":{str(onion_port)}"
        return route

    def stop_service(self):
        if self.service is not None:
            self.controller.remove_ephemeral_hidden_service(self.service.service_id)
            self.service = None