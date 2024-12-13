from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text, unique=True)
    password = db.Column(db.Text)
    name = db.Column(db.Text)
    role = db.Column(db.Text, default='owner')
    is_loyalty = db.Column(db.Boolean, default=False)
    loyalty_expire = db.Column(db.DateTime, nullable=True)
    loyalty_card = db.relationship('LoyaltyCard', backref='user', uselist=False)
    reset_code = db.Column(db.String(6), nullable=True)
    reset_code_expiry = db.Column(db.DateTime, nullable=True)

class Program(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    sale_start_datetime = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_cancelled = db.Column(db.Boolean, default=False)

class LoyaltyCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey('program.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    program = db.relationship('Program', backref='bookings')


class BookedSeat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    category = db.Column(db.Text, nullable=False) 
    row = db.Column(db.Text, nullable=False)
    number = db.Column(db.Integer, nullable=False)
    full_name = db.Column(db.Text, nullable=False)
    age = db.Column(db.Integer, nullable=False)
