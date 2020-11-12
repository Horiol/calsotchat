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
    format='%(asctime)s [%(levelname)-8s] (%(filename)-10s:%(lineno)3d) (%(name)s) %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG
)
logging.getLogger("engineio.server").setLevel(logging.WARNING)

def main(**kwargs):
    main_folder = os.path.expanduser(kwargs['data_folder'])
    if not os.path.exists(main_folder):
        os.makedirs(main_folder)
        logging.info(f"Data directory created at {main_folder}")

    logging.info(f"args: {args.__dict__}")
    logging.info("Starting services...")
    
    tor_service = Tor()
    route = tor_service.start_service(**kwargs)
    
    flask_api = MainApi(route, **kwargs)
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
        '--onion_port', 
        type=int,
        default=80,
        dest='onion_port',
        help='port to bind onion hidden service (default: 80)'
    )
    parser.add_argument(
        '--onion_control_port', 
        type=int,
        default=9051,
        dest='onion_control_port',
        help='port to bind onion hidden service (default: 9051)'
    )
    parser.add_argument(
        '--onion_socks_port', 
        type=int,
        default=9050,
        dest='onion_socks_port',
        help='port to bind onion hidden service (default: 9050)'
    )
    parser.add_argument(
        '--folder', 
        type=str,
        default='~/calsotchat',
        dest='data_folder',
        help='Directory to save data between executions (default: ~/calsotchat)'
    )
    args = parser.parse_args()
    main(**args.__dict__)