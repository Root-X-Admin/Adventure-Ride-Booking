import os
import psycopg2


class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = "postgresql://database_owner:npg_WmaM37DtPuoi@ep-floral-dust-a1bml0g0-pooler.ap-southeast-1.aws.neon.tech/database?sslmode=require&connect_timeout=20"
    # SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail Configuration
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = ''
    MAIL_PASSWORD = ''
    MAIL_DEFAULT_SENDER = ''
    MAIL_USE_SSL = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False