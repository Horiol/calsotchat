import enum
from datetime import datetime
from dataclasses import dataclass

# from backend.api import db
from db import db

rooms_contacts_association = db.Table('rooms_contacts_association',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True),
    db.Column('contact_address', db.String, db.ForeignKey('contact.address'), primary_key=True)
)

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    private = db.Column(db.Boolean, default=False)

    members = db.relationship("Contact", secondary=rooms_contacts_association)

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()

@dataclass
class Contact(db.Model):
    id: int
    address: str
    name: str
    online: bool

    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String, unique=True)
    name = db.Column(db.String, nullable=False)
    online = db.Column(db.Boolean, default=False)

    def save(self):
        if not self.id:
            db.session.add(self)
            # Create a room to talk only with this person
            private_room = Room(
                name=self.address,
                private=True # Flag to avoid showing this room in contacts list
            )
            private_room.save()
            private_room.members.append(self)

        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()


class MessageStatus(enum.Enum):
    READ = 'read'
    RECEIVED = 'received'
    DISPATCHED = 'dispatched'
    QUEUED = 'queued'

@dataclass
class Message(db.Model):
    id: int
    sender_address: str
    msg: str
    # status: str
    timestamp: datetime

    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    sender_address = db.Column(db.String, db.ForeignKey('contact.address'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    msg = db.Column(db.String, nullable=False)
    status = db.Column(db.Enum(MessageStatus), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship("Contact")
    room = db.relationship("Room")

    def save(self):
        if not self.id:
            db.session.add(self)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
        json_data = {
            'msg':self.msg,
            'room_id':self.room_id,
            'sender_address':self.sender_address,
        }
        return json_data

    
    def from_json(self, json_data):
        self.msg = json_data['msg']
        self.room_id = json_data['room_id']
        self.sender_address = json_data['sender_address']
        self.status = MessageStatus.RECEIVED