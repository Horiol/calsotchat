import time
import threading
import logging

from backend.tor import Tor
from backend.api import Api

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)-8s] (%(threadName)-10s) (%(filename)s:%(lineno)d) %(message)s',
)

def main():
    logging.info("Starting services...")
    
    tor_service = Tor()
    route = tor_service.start_service()
    logging.info(f"Onion service started and listening in {route}")
    
    flask_api = Api()
    # Start API service in new thread
    thread = threading.Thread(target=flask_api.start, args=(5000,))
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
    thread.join()

if __name__ == "__main__":
    main()