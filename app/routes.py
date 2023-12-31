'''
CS3250 - Software Development Methods and Tools - Fall 2023
Team: Team Syntax Errorz
Description: Final Project
'''

from app import app, db
from app.models import User, Task
from app.forms import SignUpForm, SignInForm, TaskForm
from app import app, db, load_user
from app.models import User, SubUser, Task
from app.forms import SignUpForm, SubUserSignUpForm, SignInForm, TaskForm
from flask import render_template, redirect, url_for, request, flash, jsonify
from flask.testing import FlaskClient
from flask_login import login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from sqlalchemy import func, distinct
import datetime, json, bcrypt, re
from flask_migrate import Migrate

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
        # Check if the user with the provided ID exists in both regular users and sub-users
        user = User.query.filter_by(id=form.id.data).first()
        subuser = SubUser.query.filter_by(id=form.id.data).first()

        # If subuser deactivated, display error message
        if subuser and subuser.status == 'Inactive':
            flash('Subuser is deactivated. Only the primary user can reactivate this account.', 'error')
            return render_template('users_signin.html', form=form)
        
        if not user and not subuser:
            # If neither regular user nor sub-user found, display an error message
            flash('ID not valid', 'error')
            return render_template('users_signin.html', form=form)

        # Check the password for regular users
        if user and user.password:
            # Make sure hashed_password is in bytes
            hashed_password = user.password.encode('utf-8') if isinstance(user.password, str) else user.password

            if bcrypt.checkpw(form.password.data.encode('utf-8'), hashed_password):
                # If the password matches, authenticate the regular user
                login_user(user)

                # Redirect to the "/tasks" page
                return redirect(url_for('list_tasks'))
            else:
                flash('Invalid password', 'error')

        # Check the password for sub-users
        if subuser and subuser.password:
            # Make sure hashed_password is in bytes
            hashed_password = subuser.password.encode('utf-8') if isinstance(subuser.password, str) else subuser.password

            if bcrypt.checkpw(form.password.data.encode('utf-8'), hashed_password):
                # If the password matches, authenticate the sub-user
                login_user(subuser)

                # Redirect to the "/tasks" page
                return redirect(url_for('list_tasks'))
            else:
                flash('Invalid password', 'error')

    return render_template('users_signin.html', form=form)

@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def list_tasks():
    
    if current_user.is_authenticated:
        form = TaskForm()
        user = None
        subuser = None 

        # Check and synchronize tasks for subusers with the primary user's tasks
        if isinstance(current_user, User):
            user = current_user
        if isinstance(current_user, SubUser):
            subuser = current_user
            primary_user_tasks = Task.query.filter_by(sub_user_id=current_user.user_id).all()
            subuser_tasks = Task.query.filter_by(sub_user_id=current_user.id).all()

            # Use titles to avoid duplicates
            primary_user_task_titles = {task.title for task in primary_user_tasks}
            subuser_task_titles = {task.title for task in subuser_tasks}
            

            # Add new tasks for the subuser if they dont exist
            for task in primary_user_tasks:
                if task.title not in subuser_task_titles:
                    new_task = Task(
                        title=task.title,
                        description=task.description,
                        due_date=task.due_date,
                        user_id=current_user.user_id,
                        sub_user_id=current_user.id
                    )
                    db.session.add(new_task)
                    db.session.commit()

            # Delete tasks that are no longer present in the primary user's task list
            for subuser_task in subuser_tasks:
                if subuser_task.title not in primary_user_task_titles:
                    db.session.delete(subuser_task) 
                    db.session.commit()

            # Check to see if description or due date has changed
            for subuser_task in subuser_tasks:
                for primary_user_task in primary_user_tasks:
                    if subuser_task.title == primary_user_task.title:
                        if subuser_task.description != primary_user_task.description or subuser_task.due_date != primary_user_task.due_date:
                            subuser_task.description = primary_user_task.description
                            subuser_task.due_date = primary_user_task.due_date
                            db.session.commit()

        if form.validate_on_submit():
            existingSubusers = SubUser.query.filter_by(user_id=current_user.id).all()

            for subuser in existingSubusers:
                # Create a new task for each subuser
                new_task = Task(
                    title=form.title.data,
                    description=form.description.data,
                    due_date=form.due_date.data,
                    user_id=current_user.id,
                    sub_user_id=subuser.id
                )

                db.session.add(new_task)
                db.session.commit()
            new_task = Task(
                title=form.title.data,
                description=form.description.data,
                due_date=form.due_date.data,
                user_id=current_user.id,
                sub_user_id=current_user.id
            )

            db.session.add(new_task)
            db.session.commit()

            flash('Task created successfully!', 'success')
            return redirect(url_for('list_tasks'))
            
        if isinstance (current_user, User):
            active_tasks = Task.query.filter_by(sub_user_id=current_user.id, completed=False).all()
            completed_tasks = Task.query.filter_by(sub_user_id=current_user.id, completed=True).all()

        elif isinstance (current_user, SubUser):
            active_tasks = Task.query.filter_by(sub_user_id=current_user.id, completed=False).all()
            completed_tasks = Task.query.filter_by(sub_user_id=current_user.id, completed=True).all()

        return render_template('tasks.html', form=form, active_tasks=active_tasks, completed_tasks=completed_tasks, subuser=subuser, user=user)

@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)

    # Ensure that only the primary user or the owner of the task can delete it
    if task.user_id == current_user.id or (task.sub_user_id == current_user.id):
        
        # If the current user is the primary user, delete all related subuser tasks
        if task.user_id == current_user.id:
            related_subuser_tasks = Task.query.filter_by(title=task.title, user_id=task.user_id).all()
            for sub_task in related_subuser_tasks:
                db.session.delete(sub_task)

        # Delete the primary user's task
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
    else:
        flash('You do not have permission to delete this task', 'error')
    
    return redirect(url_for('list_tasks'))



#route for marking tasks complete use unique IDS to prevent altering other users tasks
@app.route('/tasks/mark_complete/<int:task_id>', methods=['POST'])
@login_required
def mark_task_complete(task_id):
    task = Task.query.get_or_404(task_id)
    
    # Ensure the task belongs to the current subuser of primary user
    if (task.sub_user_id or task.user_id) != current_user.id:
        flash("You do not have permission to modify this task", "error")
        return redirect(url_for('list_tasks'))

    if current_user.is_authenticated:
        task.completed = not task.completed  # Toggle the completion status
        db.session.commit()
        flash('Task status updated.', 'success')
        return redirect(url_for('list_tasks'))


@app.route('/tasks/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash("You're not authorized to edit this task.", 'error')
        return redirect(url_for('list_tasks'))
    
    form = TaskForm(obj=task)  # Pre-populate the form with the task data
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('list_tasks'))
    
    return render_template('edit_task.html', form=form, task_id=task.id)


# route for user to create subuser
@app.route('/subuser_signup', methods=['GET', 'POST'])
@login_required
def create_subuser():
    form = SubUserSignUpForm()
    anyErrors = False

    # Check if the form has been submitted and if all fields are filled in
    if form.submit.data and not form.validate():
        flash('Please fill in all the fields', 'error')
        return render_template('subuser_signup.html', form=form)
    
    # Exception handling cases turn anyErrors to True
    # Check if the user ID is already taken by a subuser or regular user
    existing_user = User.query.filter_by(id=form.id.data).first()
    existing_subuser = SubUser.query.filter_by(id=form.id.data).first()
    existing_email_user = User.query.filter_by(email=form.email.data).first()
    existing_email_subuser = SubUser.query.filter_by(email=form.email.data).first()
    if form.validate_on_submit():
        if existing_user or existing_subuser:
            flash('ID is already taken', 'error')
            anyErrors = True

        # Check if the email is in a valid format
        if not is_valid_email(form.email.data):
            flash('Invalid email format', 'error')
            anyErrors = True

        # Check if the email is already registered to a subuser or regular user

        if existing_email_user or existing_email_subuser:
            flash('Email is already registered', 'error')
            anyErrors = True

        # Check for any errors
        if anyErrors:
            return render_template('subuser_signup.html', form=form)
        else:
            # Generate a salt and hash the password using bcrypt
            password = f"{current_user.id}{form.name.data[:3].lower()}"
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

            # Create a new subuser object and save it to the database
            new_subuser = SubUser(
                id=form.id.data,
                name=form.name.data,
                email=form.email.data,
                password=hashed_password,
                user_id=current_user.id,
                status= 'Active'
            )

            db.session.add(new_subuser)
            db.session.commit()
            # If primary user already has tasks prior to subuser creation, create tasks for subuser
            if isinstance(current_user, User):
                primary_user_tasks = Task.query.filter_by(sub_user_id=current_user.id).all()
                for task in primary_user_tasks:
                    new_task = Task(
                        title=task.title,
                        description=task.description,
                        due_date=task.due_date,
                        user_id=current_user.id,
                        sub_user_id=new_subuser.id
                    )
                    db.session.add(new_task)
                    db.session.commit()
            # Redirect to the task page
            return redirect(url_for('list_tasks'))
    return render_template('subuser_signup.html', form=form)


@app.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    # Allow primary users to view and manage subusers including deleting deactivating, and reactivating; Filter by primary user id 
    if isinstance(current_user, User):
        subusers = SubUser.query.filter_by(user_id=current_user.id).all()
        subusers_tasks = {subuser.id: Task.query.filter_by(sub_user_id=subuser.id).all() for subuser in subusers}
        return render_template('manage_users.html', subusers=subusers, subusers_tasks=subusers_tasks)
    else:
        flash('You do not have the necessary permissions to perform this action.', 'error')
        return redirect(url_for('index'))

@app.route('/deactivate_subuser/<id>', methods=['GET', 'POST'])
@login_required
def deactivate_subuser(id):
    subuser = SubUser.query.get(id)
    if subuser.user_id == current_user.id:
        # Deactivate the subuser
        subuser.status = "Inactive"
        db.session.commit()
        flash(f'Subuser {subuser.name} has been deactivated.', 'success')
    else:
        flash('Invalid action or permission denied.', 'error')

    return redirect(url_for('manage_users'))

@app.route('/reactivate_subuser/<id>', methods=['GET', 'POST'])
@login_required
def reactivate_subuser(id):
    subuser = SubUser.query.get(id)
    if subuser.user_id == current_user.id:
        # Reactivate the subuser
        subuser.status = 'Active'
        db.session.commit()
        flash(f'Subuser {subuser.name} has been reactivated.', 'success')
    else:
        flash('Invalid action or permission denied.', 'error')
    return redirect(url_for('manage_users'))

@app.route('/delete_subuser/<id>', methods=['GET', 'POST'])
@login_required
def delete_subuser(id):
    subuser = SubUser.query.get(id)
    if subuser and subuser.user_id == current_user.id:
        # Delete the subuser
        db.session.delete(subuser)
        db.session.commit()
        flash(f'Subuser {subuser.name} has been deleted.', 'success')
    else:
        flash('Invalid action or permission denied.', 'error')

    return redirect(url_for('manage_users'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))  # Redirect to the homepage or login page
