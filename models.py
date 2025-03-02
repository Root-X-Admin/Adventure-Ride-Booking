from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
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