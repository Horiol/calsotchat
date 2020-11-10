import time
import threading
import logging
import os
import argparse

from eventlet.hubs import epolls, kqueue, selects
from dns import dnssec, e164, hash, namedict, tsigkeyring, update, version, zone

from backend.tor import Tor
from backend.api import MainApi

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)-8s] (%(threadName)-10s) (%(filename)-10s:%(lineno)3d) %(message)s',
)

def main(**kwargs):
    logging.info("Starting services...")
    
    tor_service = Tor()
    route = tor_service.start_service(**kwargs)
    # logging.info(f"Onion service started and listening in {route}")
    
    flask_api = MainApi(route)
    # Start API service in new thread
    thread = threading.Thread(target=flask_api.start, args=(kwargs['port'],))
    thread.daemon = True
    thread.start()
    logging.info("API started")

    while True:
        try:
            time.sleep(24*60*60) # Wait 24h
        except KeyboardInterrupt:
            logging.info("Stopping services...")
            flask_api.stop()
            logging.debug("API stopped")
            tor_service.stop_service()
            logging.debug("Onion Service stopped")
            logging.info("Services stopped, bye")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Chat app using onion hidden services.')
    parser.add_argument(
        '--port', 
        type=int,
        default=5000,
        dest='port',
        help='local port to bind flask app (default: 5000)'
    )
    parser.add_argument(
        '--onion-port', 
        type=int,
        default=80,
        dest='onion_port',
        help='port to bind onion hidden service (default: 80)'
    )
    parser.add_argument(
        '--file', 
        type=str,
        default='my_service_key',
        dest='key_file',
        help='file name that saves the key to create a service with the same onion address (default: my_service_key)'
    )
    args = parser.parse_args()
    main(**args.__dict__)