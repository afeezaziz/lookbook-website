from authlib.integrations.flask_client import OAuth
from flask import redirect, url_for, session, request, jsonify
from app import app, db
from models import User
from datetime import datetime
import requests

oauth = OAuth(app)

google = oauth.register(
    'google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
    client_kwargs={
        'scope': 'openid email profile'
    }
)

def init_oauth_routes():
    @app.route('/login/google')
    def login_google():
        redirect_uri = url_for('authorize_google', _external=True)
        return google.authorize_redirect(redirect_uri)

    @app.route('/authorize/google')
    def authorize_google():
        try:
            token = google.authorize_access_token()
            resp = google.get('https://www.googleapis.com/oauth2/v2/userinfo')
            user_info = resp.json()

            user = User.query.filter_by(email=user_info['email']).first()

            if user:
                user.google_id = user_info.get('id')
                user.name = user_info.get('name')
                user.profile_picture = user_info.get('picture')
                user.access_token = token.get('access_token')
                user.refresh_token = token.get('refresh_token')
                user.token_expiry = datetime.fromtimestamp(token.get('expires_at')) if token.get('expires_at') else None
                user.updated_at = datetime.utcnow()
            else:
                user = User(
                    email=user_info['email'],
                    name=user_info.get('name'),
                    profile_picture=user_info.get('picture'),
                    google_id=user_info.get('id'),
                    access_token=token.get('access_token'),
                    refresh_token=token.get('refresh_token'),
                    token_expiry=datetime.fromtimestamp(token.get('expires_at')) if token.get('expires_at') else None
                )
                db.session.add(user)

            db.session.commit()

            from flask_login import login_user
            login_user(user)

            return redirect(url_for('home'))
        except Exception as e:
            return f"Error during Google OAuth: {str(e)}", 400

    @app.route('/profile')
    def profile():
        if 'google_token' not in session:
            return redirect(url_for('login_google'))

        user_info = session.get('user_info')
        return jsonify(user_info)

def apply_db_migrations():
    with app.app_context():
        try:
            from models import User
            db.create_all()
            print("Database tables created successfully!")
        except Exception as e:
            print(f"Error creating database tables: {e}")