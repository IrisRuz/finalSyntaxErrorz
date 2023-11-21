from app import app, db, load_user
from app.models import User
from app.forms import SignUpForm, SignInForm
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from sqlalchemy import func, distinct
import datetime
import json
import bcrypt

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users_signup', methods=['GET', 'POST'])
def users_signup():
    form = SignUpForm()

    if form.validate_on_submit():
        # Check if the provided passwords match
        if form.password.data == form.password_confirm.data:
            # Generate a salt and hash the password using bcrypt
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(form.password.data.encode('utf-8'), salt)

            # Create a new User object and save it to the database 
            new_user = User(
                id=form.id.data,
                email=form.email.data,
                password=hashed_password, 
            )

            db.session.add(new_user)
            db.session.commit()

            # Redirect to the index page
            return redirect(url_for('index'))

    return render_template('users_signup.html', form=form)

@app.route('/users_signin', methods=['GET', 'POST'])
def users_signin():
    form = SignInForm()

    if form.validate_on_submit():
        # Check if the user with the provided ID exists in the database
        user = User.query.filter_by(id=form.id.data).first()

        if user and user.password:
            # If the user exists and has a password, check the password
            hashed_password = user.password

            if bcrypt.checkpw(form.password.data.encode('utf-8'), hashed_password):
                # If the password matches, authenticate the user
                login_user(user)

                # Redirect to the "/catalog" page
                return redirect(url_for('catalog'))
            
    return render_template('users_signin', form=form)