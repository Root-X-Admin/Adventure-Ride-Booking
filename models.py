
from flask_login import UserMixin
from __init__ import db



class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  
    difficulty = db.Column(db.String(20), nullable=False)  
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False) 
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)  
     
     # Relationship with Booking
    bookings = db.relationship('Booking', backref='activity', lazy=True)  

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    participants = db.Column(db.Integer, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="Confirmed")  
    rewards = db.Column(db.Integer, default=0)  
    

    def mark_completed(self):
        """Marks the booking as completed and assigns reward points."""
        self.status = "Completed"
        self.rewards = self.participants * 10  

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    otp_verified = db.Column(db.Boolean, default=False) 
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class TempUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    otp = db.Column(db.String(6), nullable=False)  # Store OTP temporarily
    otp_expiry = db.Column(db.DateTime, nullable=False)  # Expiry time for OTP