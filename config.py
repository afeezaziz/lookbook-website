import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # MariaDB configuration with PyMySQL
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '3306')
    db_name = os.environ.get('DB_NAME', 'lookbook')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mariadb+pymysql://mariadb:EIy1ToVZfhxIt7uj8QkNFM4ZVVJC4ALw4q7atcCpcF23Ie15jZO0XUx4lBuOV5k4@104.248.150.75:33006/default'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth2
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

    # OAuth2 configuration
    OAUTHLIB_INSECURE_TRANSPORT = '1'  # Only for development

    # Redirect URIs
    GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"