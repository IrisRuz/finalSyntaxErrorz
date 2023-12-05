from app import db 
from flask_login import UserMixin
from datetime import datetime
import bcrypt

# create user class with id as a string, email as a string, and password as a string
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)  # Max 50 characters
    description = db.Column(db.Text, nullable=False)  # Text typically doesn't need length specified
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('tasks'))

