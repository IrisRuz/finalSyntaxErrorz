from app import db 
from flask_login import UserMixin
import bcrypt

# create user class with id as a string, email as a string, and password as a string
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
