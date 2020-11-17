import logging

from flask import Flask
from flask_restx import Api, Resource, fields, Namespace
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.exceptions import BadRequest, InternalServerError, NotFound, Conflict

from flask_cors import CORS

from backend.models import Message, Contact, Room, MessageStatus
from backend.db import db

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
        room = Room(**api.payload)
        room.save()
        logging.info(f"Room {room.name} created")

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

@api.route(f'/{rooms_ns}/<string:hash>/messages/')
class RoomMessagesResource(Resource):
    @api.marshal_list_with(message_model)
    def get(self, hash):
        # return Message.query.filter_by(room_id=id).order_by(Message.timestamp).all()
        return Message.query.filter_by(room_hash=hash).order_by(Message.timestamp.desc()).limit(10).all()