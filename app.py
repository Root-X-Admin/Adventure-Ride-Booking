from flask import Flask
from config import Config
from models import db
from routes import booking_bp
from dashboard_routes import dashboard_bp

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Import and register routes after initializing db
from routes import app_routes
# db.init_app(app)
app.register_blueprint(booking_bp)
app.register_blueprint(app_routes)
app.register_blueprint(dashboard_bp)

if __name__ == "__main__":
    app.run(debug=True)