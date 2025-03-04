# from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from __init__ import db

# db = SQLAlchemy()

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # e.g., Water, Land, Air
    difficulty = db.Column(db.String(20), nullable=False)  # Beginner, Intermediate, Advanced
    price = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)  # Link to activity image
    description = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Float, nullable=False)  # Store average rating
     
     # Relationship with Booking
    bookings = db.relationship('Booking', backref='activity', lazy=True)  # ✅ Add this

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
    status = db.Column(db.String(20), default="Confirmed")  # Confirmed, Completed, Cancelled
    rewards = db.Column(db.Integer, default=0)  # Reward points earned
    

    def mark_completed(self):
        """Marks the booking as completed and assigns reward points."""
        self.status = "Completed"
        self.rewards = self.participants * 10  # Example: 10 points per participant

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"