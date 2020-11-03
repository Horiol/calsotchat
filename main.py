import time
import threading

from backend.tor import Tor
from backend.api import Api

def main():
    print("Starting services...")
    
    tor_service = Tor()
    route = tor_service.start_service()
    print(f"Onion service started and listening in {route}")
    
    flask_api = Api()
    # Start API service in new thread
    t = threading.Thread(target=flask_api.start, args=(5000,))
    t.daemon = True
    t.start()
    print("API started")

    while True:
        try:
            time.sleep(24*60*60) # Wait 24h
        except KeyboardInterrupt:
            print("Stopping services...")
            flask_api.stop()
            print("API stopped")
            tor_service.stop_service()
            print("Onion Service stopped")
            break

if __name__ == "__main__":
    main()