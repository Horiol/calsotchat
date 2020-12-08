
json_headers = {
    'Content-Type': 'application/json'
}

def create_room_to_member(onion_session, member, room_json):
    try:
        onion_session.post(
            f'http://{member.address}/api/rooms/', 
            data=room_json,
            headers=json_headers
        )
    except:
        pass # TODO: save member and room to retry
        
def remove_room_to_member(onion_session, member, room_json):
    try:
        onion_session.delete(
            f'http://{member.address}/api/rooms/{room_json["hash"]}/'
        )
    except:
        pass # TODO: save member and room to retry