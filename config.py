import os

class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail Configuration
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'ashande29@gmail.com'
    MAIL_PASSWORD = 'yequetiqbwqyztyc'
    # MAIL_DEFAULT_SENDER = 'ashande29@gmail.com'
    MAIL_USE_SSL = True
