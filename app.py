from flask import Flask, current_app
from flask_mail import Mail
from config import Config
from models import db, User  # Ensure User is imported here
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from __init__ import create_app

app = create_app()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Initialize Flask extensions
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'app_routes.login'  # Ensuring proper redirection

# Define user loader function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Ensure User is imported

# Import blueprints AFTER initializing app & db to prevent circular imports
from routes import app_routes, booking_bp

app.register_blueprint(app_routes)
app.register_blueprint(booking_bp)

mail = Mail(app )

@app.route("/check_mail_config")
def check_mail_config():
    return f"MAIL USERNAME: {current_app.config.get('MAIL_USERNAME')}"

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensure tables exist
    app.run(debug=True)
