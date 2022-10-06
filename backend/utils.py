
import logging
import json


json_headers = {
    'Content-Type': 'application/json'
}

def create_room_to_member(onion_session, member, room_json):
    try:
        response = onion_session.post(
            f'http://{member.address}/api/rooms/', 
            data=json.dumps(room_json),
            headers=json_headers
        )
        logging.info(response.content)
    except Exception as e:
        logging.exception(e)
        
def remove_room_to_member(onion_session, member, room_json):
    try:
        response = onion_session.delete(
            f'http://{member.address}/api/rooms/{room_json["hash"]}/'
        )
        logging.info(response.content)
    except Exception as e:
        logging.exception(e)