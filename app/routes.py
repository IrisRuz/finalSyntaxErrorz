from app import app, db, load_user
from app.models import User, Task
from app.forms import SignUpForm, SignInForm, TaskForm
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from sqlalchemy import func, distinct
import datetime, json, bcrypt, re

@app.route('/')
def index():
    return render_template('index.html')

def is_valid_email(email):
    # Basic email format validation using regex(Regular Expressions)
    email_regex = r'^[a-zA-Z0-9_.-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None

@app.route('/users_signup', methods=['GET', 'POST'])
def users_signup():
    form = SignUpForm()
    anyErrors = False

    # Check if the form has been submitted and if all fields are filled in
    if form.submit.data and not form.validate():
        flash('Please fill in all the fields', 'error')
        return render_template('users_signup.html', form=form)

    if form.validate_on_submit():
        # Exception handling cases turn anyErrors to True

        # Check if the user ID is already taken
        existing_user = User.query.filter_by(id=form.id.data).first()
        if existing_user:
            flash('ID is already taken', 'error')
            anyErrors = True
        
        # Check if the email is in a valid format
        if not is_valid_email(form.email.data):
            flash('Invalid email format', 'error')
            anyErrors = True

        # Check if the email is already registered
        existing_email_user = User.query.filter_by(email=form.email.data).first()
        if existing_email_user:
            flash('Email is already registered', 'error')
            anyErrors = True

        # Check if the password and password confirmation match
        if form.password.data != form.password_confirm.data:
            flash('Passwords do not match', 'error')
            anyErrors = True
        
        # Check for any errors
        if anyErrors:
            return render_template('users_signup.html', form=form)

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

        if not user:
            # If the user does not exist, display an error message
            flash('ID not valid', 'error')
            
        if user and user.password:
            # If the user exists and has a password, check the password
            hashed_password = user.password

            if bcrypt.checkpw(form.password.data.encode('utf-8'), hashed_password):
                # If the password matches, authenticate the user
                login_user(user)

                # Redirect to the "/tasks" page
                return redirect(url_for('list_tasks'))
            else:
                flash('Invalid password', 'error')

    return render_template('users_signin.html', form=form)
    
def get_next_task_number():
    # Retrieve the maximum order number from the database and increment it by 1
    max_task_number = db.session.query(func.max(Task.id)).scalar()
    if max_task_number is None:
        max_task_number = 0
    return max_task_number + 1

@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def list_tasks():
    user_tasks = Task.query.filter_by(user_id=current_user.id).all()
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
    
    return render_template('tasks.html', form=form, tasks=user_tasks)

# delete existing tasks
@app.route('/tasks/delete/<task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if task:
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    else:
        flash('Task not found!', 'error')
    return redirect(url_for('list_tasks'))

#route for marking tasks complete
@app.route('/tasks/mark_complete/<int:task_id>', methods=['POST'])
@login_required
def mark_task_complete(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("You do not have permission to modify this task", "error")
        return redirect(url_for('list_tasks'))
    
    task.completed = not task.completed
    db.session.commit()
    flash('Task status updated.', 'success')
    return redirect(url_for('list_tasks'))