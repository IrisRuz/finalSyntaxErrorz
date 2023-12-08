'''
<<<<<<< HEAD
CS3250 - Software Development Methods and Tools - Project 3 Final
Team:SyntaxErrorz
Description: Project 3 User Task Management
=======
CS3250 - Software Development Methods and Tools - Fall 2023
Team: Team Syntax Errorz
Description: Final Project
>>>>>>> dev
'''

from app import db
from flask_login import UserMixin
from datetime import datetime
import bcrypt

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    
class SubUser(db.Model, UserMixin):
    __tablename__ = 'sub_users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
                  
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    sub_user_id = db.Column(db.String, db.ForeignKey('sub_users.id'))  
    user = db.relationship('User', backref=db.backref('tasks'))
    sub_user = db.relationship('SubUser', backref=db.backref('tasks'))
    completed_by_subuser = db.Column(db.Boolean, default=False)

