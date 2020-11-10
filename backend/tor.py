import time
import shlex
import os
import logging

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

    def start_service(self, onion_port=80, port=5000, key_file=None, **kwargs):
        """Start Onion Hidden Services

        Args:
            port (int): local port that will be listenint the service

        Returns:
            str: onion address assigned to this service
        """
        if self.service is None:
            self.controller = Controller.from_port(port=self.tor_control_port)
            self.controller.authenticate()

            if key_file:
                key_path = os.path.expanduser(f'~/calsotchat/{key_file}')

                ### If file does not exist create it and use it to create an onion hidden service
                if not os.path.exists(key_path):
                    self.service = self.controller.create_ephemeral_hidden_service(
                        {onion_port: port}, 
                        await_publication = True
                    )
                    logging.info("Started a new hidden service with the address of %s.onion" % self.service.service_id)

                    with open(key_path, 'w') as key_file:
                        key_file.write('%s:%s' % (self.service.private_key_type, self.service.private_key))
                
                
                ### If file already exist use it to resume the same onion address
                else:
                    with open(key_path) as key_file:
                        key_type, key_content = key_file.read().split(':', 1)

                    self.service = self.controller.create_ephemeral_hidden_service(
                        {onion_port: port}, 
                        key_type = key_type, 
                        key_content = key_content, 
                        await_publication = True
                    )
                    logging.info("Resumed %s.onion" % self.service.service_id)
            else:
                # Create Onion Hidden Service
                self.service = self.controller.create_ephemeral_hidden_service(
                    {onion_port: port}, 
                    await_publication = True
                )
                logging.info("Started a new hidden service with the address of %s.onion" % self.service.service_id)

            
        # return onion route
        route = self.service.service_id + ".onion"
        if onion_port != 80:
            route += ":" + str(onion_port)
        return route

    def stop_service(self):
        if self.service is not None:
            self.controller.remove_ephemeral_hidden_service(self.service.service_id)
            self.service = None