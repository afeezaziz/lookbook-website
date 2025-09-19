from flask import Flask, render_template, redirect, url_for, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from authlib.integrations.flask_client import OAuth
from config import Config
from datetime import datetime
from extensions import db
from models import User

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
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

# User model moved to models.py (imported at top)

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

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/looks')
def looks():
    return render_template('look.html')

@app.route('/looks/<int:lookId>')
def look_detail(lookId):
    # Pass lookId to the template if needed in the future
    return render_template('look.html', lookId=lookId)

@app.route('/items')
def items():
    return render_template('item.html')

@app.route('/items/<int:itemId>')
def item_detail(itemId):
    # Pass itemId to the template if needed in the future
    return render_template('item.html', itemId=itemId)

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