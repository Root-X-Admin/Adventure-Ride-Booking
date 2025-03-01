from flask import Flask
from config import Config
from models import db

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Import and register Blueprints
from routes import app_routes
app.register_blueprint(app_routes)
