from app import app, db, load_user
from app.models import User, Task
from app.forms import SignUpForm, SignInForm, TaskForm
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

@app.route('/users/signin', methods=['GET', 'POST'])
def users_signin():
    form = SignInForm()
    if form.validate_on_submit(): 
        try: 
            user = load_user(form.id.data)
            print(user)
            if bcrypt.checkpw(
                form.password.data.encode('utf-8'), 
                user.password
            ): 
                login_user(user)
                return redirect(url_for('list_tasks'))
            else:
                return '<p>Wrong password!</p>'
        except Exception as ex: 
                return f'<p>Could not find a user with the given id: {ex}</p>'
    else:
        return render_template('users_signin.html', form=form)
    
def get_next_task_number():
    # Retrieve the maximum order number from the database and increment it by 1
    max_task_number = db.session.query(func.max(Task.id)).scalar()
    if max_task_number is None:
        max_task_number = 0
    return max_task_number + 1

@app.route('/task/create', methods=['GET', 'POST'])  
def create_task():
    form = TaskForm()

    if form.validate_on_submit():
        new_task = Task(
            id = get_next_task_number(),
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            user_id=current_user.id,
            user = current_user
        )

        db.session.add(new_task)
        db.session.commit()

        flash('Task created successfully!', 'success')
        return redirect(url_for('list_tasks'))
    else:
        print(form.errors)
    return render_template('create_task.html', form=form)
    
@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def list_tasks():
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('tasks.html', tasks=user_tasks)