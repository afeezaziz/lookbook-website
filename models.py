from datetime import datetime
from flask_login import UserMixin
from extensions import db


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
