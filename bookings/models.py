from bookings import db
from datetime import datetime
from sqlalchemy import Enum, DateTime
from flask_login import UserMixin, AnonymousUserMixin
from enum import Enum

class Anonymous(AnonymousUserMixin):
  def __init__(self):
    self.name = 'Guest'

class EventStatus(Enum):
    UPCOMING = 1
    CANCELLED = 2
    BOOKED = 3
    INACTIVE = 4

#this could be populated from whatever the current values in the database are (but risks
# 'dirty' inputs from users...)
class EventGenre(Enum):
    DANCE = 1
    JAZZ = 2
    POP = 3
    REGGAE = 4
    ROCK = 5
    OTHER = 6

class EventCity(Enum):
    BRISBANE = 1
    MELBOURNE = 2
    SYDNEY = 3
    PERTH = 4
    ADELAIDE = 5

class User(UserMixin,db.Model):
    __tablename__ = 'users' # good practice to specify table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), index=True, unique=True, nullable=False)
    emailid = db.Column(db.String(100), index=True, nullable=False)
	#password is never stored in the DB, an encrypted password is stored
	# the storage should be at least 255 chars long
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    # relation to call user.comments and comment.created_by
    comments = db.relationship('Comment', backref='user')
    created_events = db.relationship('Event', backref='user')
    created_bookings = db.relationship('Booking', backref='user')

    def __repr__(self):
        str = 'Name: {0}. Email: {1}'
        str.format(self.name, self.emailid)
        return str

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), index=True, unique=True, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    headliner = db.Column(db.String(80), index=True, nullable=False)
    venue = db.Column(db.String(80))
    description = db.Column(db.String(2000), nullable=False)
    image = db.Column(db.String(400), default='/static/images/live.jpg')
    total_tickets = db.Column(db.Integer, nullable=False)
    tickets_remaining = db.Column(db.Integer)
    event_status = db.Column(db.Enum(EventStatus))
    event_genre = db.Column(db.Enum(EventGenre))
    event_city = db.Column(db.Enum(EventCity))
    created_on = db.Column(db.DateTime, default=datetime.now())
    # ... Create the Comments db.relationship
	# relation to call event.comments and comment.event
    comments = db.relationship('Comment', backref='event')
    users = db.relationship('User', backref='event')
    #FK
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        str = 'Title: {0}, Date: {1}'
        str.format(self.title, self.date)
        return str

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(400))
    created_at = db.Column(db.DateTime, default=datetime.now())
    #add the foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))

    def __repr__(self):
        return "<Comment: {}>".format(self.text)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key = True)
    tickets_booked = db.Column(db.Integer, nullable = False)
    booked_on = db.Column(db.DateTime, default=datetime.now())
    bookings = db.relationship('Event', backref='bookings')
    #FK's
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.id'))
