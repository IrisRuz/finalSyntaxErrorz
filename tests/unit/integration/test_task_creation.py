# test_task_creation.py
import pytest
from flask_bcrypt import Bcrypt
from app import app, db  # Import the Flask app instance and db directly
from app.models import Task, User
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

@pytest.fixture(scope='module')
def test_client():
    # Configure the Flask app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for the tests
    
    # Establish an application context
    ctx = app.app_context()
    ctx.push()

    # Initialize Bcrypt
    bcrypt = Bcrypt(app)

    # Create the database and load test data
    db.create_all()

    # Create a test user with all required fields
    hashed_password = bcrypt.generate_password_hash('testpassword').decode('utf-8')
    test_user = User(id='testuser', email='test@example.com', password=hashed_password)  # Make sure to include the email if it's a required field

    db.session.add(test_user)
    db.session.commit()

    with app.test_client() as test_client:
        yield test_client  # This is where the testing happens!

    db.drop_all()  # Cleanup after tests run
    ctx.pop()

def test_task_creation_and_deletion(test_client):
    # Log in
    login_response = test_client.post('/users_signin', data={
        'id': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert login_response.status_code == 200

    # Extract CSRF token from login response if needed
    soup = BeautifulSoup(login_response.data, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'}).get('value') if soup.find('input', {'name': 'csrf_token'}) else None

    # Create a task with or without CSRF token
    task_creation_data = {
        'title': 'Test Task',
        'description': 'This is a test task.',
        'due_date': (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d')
    }
    if csrf_token:
        task_creation_data['csrf_token'] = csrf_token

    task_creation_response = test_client.post('/tasks', data=task_creation_data, follow_redirects=True)
    assert task_creation_response.status_code == 200

    # Retrieve the task to get its ID
    task = Task.query.filter_by(title='Test Task').first()
    assert task is not None

    # Delete the task
    task_deletion_response = test_client.post(f'/tasks/delete/{task.id}', data={
        'csrf_token': csrf_token
    }, follow_redirects=True)
    assert task_deletion_response.status_code == 200

    # Check if the task was deleted
    deleted_task = Task.query.get(task.id)
    assert deleted_task is None