import unittest
from app import app, db
from app.models import User, Task
from flask_login import login_user
import bcrypt

class TaskRouteTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        salt = bcrypt.gensalt()
        password = 'testpassword'.encode('utf-8')
        hashed_password = bcrypt.hashpw(password, salt)
        self.test_user = User(id='testuser',email='testemail@example.com',password=hashed_password)
        db.session.add(self.test_user)
        db.session.commit()

        login_page_response = self.app.get('/users_signin')
        soup = BeautifulSoup(login_page_response.data, 'html.parser')
        csrf_token = soup.find('input', id='csrf_token')['value']


        login_response = self.app.post('/users_signin', data={
            'id': 'testuser',  
            'password': 'testpassword',
            'csrf_token': csrf_token
        }, follow_redirects=True)
        print("login response:", login_response.data)
        print("Login response status code:", login_response.status_code)
        print("Login response data:", login_response.data.decode('utf-8'))

        self.test_task = Task(id =1, user_id=self.test_user.id, title='Test Task Title', description='test description',completed= False )
        db.session.add(self.test_task)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_mark_task_complete(self):
        print("Initial Task Completed Status:", self.test_task.completed)
        form_data = {'completed': 'on'}
        response = self.app.post(f'/tasks/mark_complete/{self.test_task.id}', 
                             data=form_data, follow_redirects=True)
        
        updated_task = Task.query.filter_by(id=self.test_task.id).first()
        print("Form Data:", form_data)
        print("Response Status Code:", response.status_code)
        print("Updated Task ID:", updated_task.id)
        print("Updated Task Completed Status:", updated_task.completed)
        print("Test User ID:", self.test_user.id)
        print("Task User ID:", updated_task.user_id)
        print("Response Data:", response.data)

        self.assertTrue(updated_task.completed, "Task was not marked as completed")
        self.assertIn(b'Task status updated.', response.data)

if __name__ == '__main__':
    unittest.main()
