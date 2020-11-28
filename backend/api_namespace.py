import logging

from flask import g
from flask_restx import Resource, fields, Namespace, marshal
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound, Conflict

from flask_cors import CORS

from backend.models import Message, Contact, Room, MessageStatus
from backend.db import db
from backend.utils import create_room_to_member

api = Namespace('Api', description='')

contacts_ns = 'contacts'
messages_ns = 'messages'
rooms_ns = 'rooms'

contact_model = api.model('Contact', {
    'id': fields.Integer(readonly=True),
    'address': fields.String(required=True),
    'name': fields.String(required=True),
    'nickname': fields.String(required=True),
    'online': fields.Boolean(readonly=True),
})

room_model = api.model('Room', {
    'id': fields.Integer(readonly=True),
    'hash': fields.String(readonly=True),
    'name': fields.String(),
    'admin_address': fields.String(),
    'members': fields.List(fields.Nested(contact_model, readonly=True))
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
    # 'room': fields.Nested(room_model, readonly=True),
})

@api.route(f'/myself/')
class MyselfResource(Resource):
    @api.marshal_with(contact_model)
    def get(self):
        return Contact.query.filter_by(address=g.origin).first()

@api.route(f'/{contacts_ns}/')
class ContactResource(Resource):
    @api.marshal_list_with(contact_model)
    def get(self):
        return Contact.query.all()

    @api.expect(contact_model, validate=True)
    @api.marshal_with(contact_model, code=201)
    def post(self):
        contact = Contact.query.filter_by(address=api.payload['address']).first()
        if contact:
            raise Conflict("Contact address already in DB")

        contact = Contact(**api.payload)
        contact.save()
        logging.info(f"Contact {contact.name} created")

        return contact

@api.route(f'/{contacts_ns}/<string:address>/')
class ContactInstanceResource(Resource):
    @api.marshal_with(contact_model)
    def get(self, address):
        return Contact.query.filter_by(address=address).first()

    @api.response(204, 'Item deleted')
    def delete(self, address):
        contact = Contact.query.filter_by(address=address).first()
        if contact:
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
        message = Message.query.get(id)
        if message:
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
            api.payload["hash"] = f"{api.payload['name'].replace(' ', '_')}_{g.origin}"
            api.payload["admin_address"] = g.origin
            is_mine = True
        
        room = Room.query.filter_by(hash=api.payload["hash"]).first()
        if room:
            raise Conflict("Room name not available")

        members = []
        try:
            members = api.payload["members"]
            del api.payload["members"]
        except:
            pass

        room = Room(**api.payload)

        me = Contact.query.filter_by(address=g.origin).first()
        room.members.append(me)

        for member in members:
            contact = Contact.query.filter_by(address=member["address"]).first()
            if not contact:
                try:
                    del member["name"]
                except:
                    pass
                try:
                    del member["id"]
                except:
                    pass

                contact = Contact(**member)
                contact.save()

            room.members.append(contact)
        room.save()
        logging.info(f"Room {room.name} created")

        room_json = marshal(room, room_model)
        if is_mine:
            for member in room.members:
                if member.address != g.origin:
                    create_room_to_member(g.onion_session, member, room_json)
        g.socketio.emit('newRoom', room_json, namespace="/api/internal")
        return room

@api.route(f'/{rooms_ns}/<string:hash>/')
class RoomInstanceResource(Resource):
    @api.marshal_with(room_model)
    def get(self, hash):
        room = Room.query.filter_by(hash=hash).first()
        if not room:
            raise NotFound()
        return room

    @api.response(204, 'Item deleted')
    def delete(self, hash):
        room = Room.query.filter_by(hash=hash).first()
        if room:
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
            if user.address != g.origin:
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

        for user in api.payload['members']:
            user_object = Contact.query.get(user)
            if user_object.address != g.origin:
                room.members.remove(user_object)
        room.save()

        return room