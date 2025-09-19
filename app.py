from flask import Flask, render_template, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# OAuth setup
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

# User model
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    profile_picture = db.Column(db.String(255))
    google_id = db.Column(db.String(50), unique=True)
    access_token = db.Column(db.String(255))
    refresh_token = db.Column(db.String(255))
    token_expiry = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

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
        login_user(user)

        return redirect(url_for('home'))
    except Exception as e:
        return f"Error during Google OAuth: {str(e)}", 400

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return jsonify({
        'email': current_user.email,
        'name': current_user.name,
        'profile_picture': current_user.profile_picture
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    app.run(debug=True)