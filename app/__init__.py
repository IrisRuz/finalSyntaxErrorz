from flask import Flask
import os

app = Flask("Authentication Web App")
app.secret_key = os.environ['SECRET_KEY']

# db initialization
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db.init_app(app)

from app import models
with app.app_context(): 
    db.create_all()

# login manager
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

from app.models import User, SubUser

# user_loader callback
@login_manager.user_loader
def load_user(id):
    user = User.query.get(id)
    if user is None:
        user = SubUser.query.get(id)
    return user


from app import routes

