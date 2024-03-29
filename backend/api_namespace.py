import logging
import string
import secrets
import json

from flask import g
from flask_restx import Resource, fields, Namespace, marshal
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound, Conflict

from flask_cors import CORS

from backend.models import Message, Contact, Myself, Room, MessageStatus
from backend.db import db
from backend.utils import create_room_to_member, remove_room_to_member

CA_ROUTE = "http://qqjoe6z7ggiaq6psru5zbieohwurmkyvb6lzy3qvf3fd7bmytikh2fqd.onion"

class NullableString(fields.String):
    __schema_type__ = ['string', 'null']
    __schema_example__ = 'nullable string'

api = Namespace('Api', description='')

contacts_ns = 'contacts'
messages_ns = 'messages'
rooms_ns = 'rooms'

contact_model = api.model('Contact', {
    'id': fields.Integer(readonly=True),
    'address': fields.String(required=True),
    'name': NullableString(),
    'nickname': fields.String(required=True),
    'online': fields.Boolean(readonly=True),
})

room_model = api.model('Room', {
    'id': fields.Integer(readonly=True),
    'hash': fields.String(readonly=True),
    'name': fields.String(),
    'admin_address': fields.String(),
    'members': fields.List(fields.Nested(contact_model, readonly=True)),
    'private': fields.Boolean(readonly=True),
})

message_model = api.model('Message', {
    'id': fields.Integer(readonly=True),
    'sender_address': fields.String(),
    'sender_nickname': fields.String(),
    'room_hash': fields.String(),
    'msg': fields.String(),
    'status': fields.String(attribute=lambda x: str(MessageStatus(x.status).name), readonly=True),
    'timestamp': fields.DateTime(readonly=True),
    'sender': fields.Nested(contact_model, readonly=True),
    'room': fields.Nested(room_model, readonly=True),
})

myself_model = api.model('Myself', {
    'id': fields.Integer(readonly=True),
    'address': fields.String(readonly=True),
    'email': fields.String(required=True),
})

def create_contact(json_data):
    contact = Contact.query.filter_by(address=json_data['address']).first()
    if contact:
        # Check if room exist or was deleted
        contact_room = Room.query.filter_by(hash=json_data['address']).first()
        if contact_room:
            raise Conflict("Contact address already in DB")
        
        contact_room = Room(
            name=contact.name or contact.nickname,
            hash=contact.address,
            private=True
        )
        contact_room.save()
        contact_room.members.append(contact)
        contact_room.save()

    else:
        contact = Contact(**json_data)
        contact_room = contact.save()
        logging.info(f"Contact {contact.name} created")

    g.socketio.emit('newContact', marshal(contact_room, room_model), namespace="/api/internal")

    return contact

@api.route('/find_contact/')
class FindResource(Resource):
    def post(self):
        payload = {
            "email": api.payload['email'],
        }
        result = g.onion_session.post(
            f"{CA_ROUTE}/find_contact/",
            data=json.dumps(payload),
            headers={
                'Content-Type': 'application/json',
                'Api-Token': api.payload['api_token']
            }
        )
        if result.status_code != 200:
            return result.json(), result.status_code
        data = result.json()
        data['address'] = data.pop('onion_address')

        contact = create_contact(data)

        return marshal(contact, contact_model)

@api.route('/myself/')
class MyselfResource(Resource):
    # @api.marshal_with(contact_model)
    def get(self):
        myself = marshal(Myself.query.filter_by(address=g.origin).first(), myself_model)
        contact = marshal(Contact.query.filter_by(address=g.origin).first(), contact_model)
        api_token = None

        # Get info from CA if email in myself table
        if myself['email']:
            payload = {
                "email": myself['email'],
                "nickname": contact['nickname'],
                "onion_address": g.origin
            }
            result = g.onion_session.post(
                f"{CA_ROUTE}/contacts/",
                data=json.dumps(payload),
                headers={
                    'Content-Type': 'application/json'
                }
            )
            api_token = result.json()['api_token']

        return {
            'contact': contact,
            'api_token': api_token
        }
    
    @api.expect(myself_model, validate=True)
    def put(self):
        contact = marshal(Contact.query.filter_by(address=g.origin).first(), contact_model)
        api_token = None

        myself = Myself.query.filter_by(address=g.origin).first()
        myself.update(**api.payload)

        if myself.email:
            payload = {
                "email": myself.email,
                "nickname": contact['nickname'],
                "onion_address": g.origin
            }
            result = g.onion_session.post(
                "http://qqjoe6z7ggiaq6psru5zbieohwurmkyvb6lzy3qvf3fd7bmytikh2fqd.onion/contacts/",
                data=json.dumps(payload),
                headers={
                    'Content-Type': 'application/json'
                }
            )
            api_token = result.json()['api_token']

        return {
            'contact': contact,
            'api_token': api_token
        }

@api.route(f'/{contacts_ns}/')
class ContactResource(Resource):
    @api.marshal_list_with(contact_model)
    def get(self):
        return Contact.query.all()

    @api.expect(contact_model, validate=True)
    @api.marshal_with(contact_model, code=201)
    def post(self):
        return create_contact(api.payload)

@api.route(f'/{contacts_ns}/<string:address>/')
class ContactInstanceResource(Resource):
    @api.marshal_with(contact_model)
    def get(self, address):
        return Contact.query.filter_by(address=address).first()

    @api.response(204, 'Item deleted')
    def delete(self, address):
        if contact := Contact.query.filter_by(address=address).first():
            contact.delete()
        return '', 204

    @api.expect(contact_model, validate=True)
    @api.marshal_with(contact_model)
    def put(self, address):
        contact = Contact.query.filter_by(address=address).first()
        if not contact:
            raise NotFound()

        contact.update(**api.payload)
        return contact


@api.route(f'/{messages_ns}/')
class MessageResource(Resource):
    @api.marshal_list_with(message_model)
    def get(self):
        return Message.query.all()

@api.route(f'/{messages_ns}/<int:id>/')
class MessageInstanceResource(Resource):
    @api.marshal_with(message_model)
    def get(self, id):
        return Message.query.get(id)

    @api.response(204, 'Item deleted')
    def delete(self, id):
        if message := Message.query.get(id):
            message.delete()
        return '', 204




@api.route(f'/{rooms_ns}/')
class RoomResource(Resource):
    @api.marshal_list_with(room_model)
    def get(self):
        return Room.query.all()

    @api.expect(room_model, validate=True)
    @api.marshal_with(room_model, code=201)
    def post(self):
        api.payload["private"] = False
        is_mine = False

        if not api.payload.get("hash", None):
            alphabet = string.ascii_letters + string.digits

            is_not_unique = True
            while is_not_unique:
                salt = ''.join(secrets.choice(alphabet) for _ in range(12))

                api.payload["hash"] = f"{salt}_{g.origin}"
                room = Room.query.filter_by(hash=api.payload["hash"]).first()
                if not room:
                    is_not_unique = False

            api.payload["admin_address"] = g.origin
            is_mine = True

        members = api.payload.pop("members", [])

        room = Room(**api.payload)

        me = Contact.query.filter_by(address=g.origin).first()
        room.members.append(me)

        for member in members:
            contact = Contact.query.filter_by(address=member["address"]).first()
            if not contact:
                member.pop("name", None)
                member.pop("id", None)

                contact = Contact(**member)
                contact_room = contact.save()

                # Emit new contact event
                g.socketio.emit('newContact', marshal(contact_room, room_model), namespace="/api/internal")

            room.members.append(contact)
        room.save()
        logging.info(f"Room {room.name} created")

        room_json = marshal(room, room_model)
        if is_mine:
            for member in room.members:
                if member.address != g.origin:
                    create_room_to_member(g.onion_session, member, room_json)
        g.socketio.emit('newContact', room_json, namespace="/api/internal")
        return room

@api.route(f'/{rooms_ns}/<string:hash>/')
class RoomInstanceResource(Resource):
    @api.marshal_with(room_model)
    def get(self, hash):
        if room := Room.query.filter_by(hash=hash).first():
            return room
        else:
            raise NotFound()

    @api.response(204, 'Item deleted')
    def delete(self, hash):
        if room := Room.query.filter_by(hash=hash).first():
            room.delete()
        return '', 204
    
    @api.expect(room_model, validate=True)
    @api.marshal_with(room_model)
    def put(self, hash):
        room = Room.query.filter_by(hash=hash).first()
        if not room:
            raise NotFound()

        room.update(**api.payload)

        if 'name' in api.payload and room.private:
            # Update user name
            user = room.members[0]
            user.update(name=api.payload["name"])
        return room

@api.route(f'/{rooms_ns}/<string:hash>/messages/')
class RoomMessagesResource(Resource):
    @api.marshal_list_with(message_model)
    def get(self, hash):
        # return Message.query.filter_by(room_id=id).order_by(Message.timestamp).all()
        return Message.query.filter_by(room_hash=hash).order_by(Message.timestamp.desc()).limit(10).all()

@api.route(f'/{rooms_ns}/<string:hash>/members/')
class RoomMembersResource(Resource):
    # TODO: apply changes to all members of the group
    @api.marshal_with(room_model)
    def post(self, hash):
        room = Room.query.filter_by(hash=hash).first()
        if not room:
            raise NotFound()
        if room.admin_address != g.origin:
            raise BadRequest("You are not the room owner")

        room_json = marshal(room, room_model)
        for user in api.payload['members']:
            user_object = Contact.query.get(user)
            room.members.append(user_object)
            if user_object.address != g.origin:
                create_room_to_member(g.onion_session, user_object, room_json)
        room.save()

        return room
    
    @api.marshal_with(room_model)
    def delete(self, hash):
        room = Room.query.filter_by(hash=hash).first()
        if not room:
            raise NotFound()
        if room.admin_address != g.origin:
            raise BadRequest("You are not the room owner")

        room_json = marshal(room, room_model)
        for user in api.payload['members']:
            user_object = Contact.query.get(user)
            if user_object.address != g.origin:
                remove_room_to_member(g.onion_session, user_object, room_json)
                room.members.remove(user_object)
        room.save()

        return room

