import enum
from datetime import datetime

from backend.db import db

rooms_contacts_association = db.Table('rooms_contacts_association',
    db.Column('room_id', db.Integer, db.ForeignKey('room.id'), primary_key=True),
    db.Column('contact_address', db.String, db.ForeignKey('contact.address'), primary_key=True)
)

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String, unique=True)
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

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

class Contact(db.Model):
    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String, unique=True)
    name = db.Column(db.String, nullable=True)
    nickname = db.Column(db.String, nullable=False)
    online = db.Column(db.Boolean, default=False)

    def save(self):
        private_room = None
        if not self.id:
            db.session.add(self)
            # Create a room to talk only with this person
            private_room = Room(
                name=self.name or self.nickname,
                hash=self.address,
                private=True # Flag to avoid showing this room in contacts list
            )
            private_room.save()
            private_room.members.append(self)

        db.session.commit()

        return private_room

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()
        
        private_room = Room.query.filter_by(hash=self.address).first()
        private_room.update(name=self.name)

class MessageStatus(enum.Enum):
    READ = 'READ'
    RECEIVED = 'RECEIVED'
    DISPATCHED = 'DISPATCHED'
    QUEUED = 'QUEUED'

class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    sender_address = db.Column(db.String, db.ForeignKey('contact.address'))
    sender_nickname = db.Column(db.String, nullable=False)
    room_hash = db.Column(db.String, db.ForeignKey('room.hash'))
    msg = db.Column(db.String, nullable=False)
    status = db.Column(db.Enum(MessageStatus))
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
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()