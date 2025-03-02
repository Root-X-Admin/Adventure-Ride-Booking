from flask import Flask
from config import Config
from models import db

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Import and register routes after initializing db
from routes import app_routes
app.register_blueprint(app_routes)

if __name__ == "__main__":
    app.run(debug=True)