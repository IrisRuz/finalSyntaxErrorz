import unittest
from app import app, db
from app.models import User, Task
from flask_login import login_user

class TaskRouteTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

        test_user = User(id='testUser2005',email='testemail7@example.com',password='testpassword1')
        test_task = Task(id =895, user_id=test_user.id, title='Test Task Title', description='test description',completed= False )
        db.session.add(test_user)
        db.session.add(test_task)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_mark_task_complete(self):
        response = self.app.post('/tasks/mark_complete/895', follow_redirects=True)
        test_task = db.session.query(Task).filter_by(id=895).first()
        self.assertTrue(test_task.completed)
        self.assertIn(b'Task status updated.', response.data)

if __name__ == '__main__':
    unittest.main()
