from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail

# Initialize Flask extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'app_routes.login'  # Redirect to login if not authenticated
mail = Mail()  # Initialize Flask-Mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)  # Initialize Flask-Mail

    # Import Blueprints inside the function to prevent circular imports
    from routes import app_routes, booking_bp

    app.register_blueprint(app_routes)
    app.register_blueprint(booking_bp)

    return app
