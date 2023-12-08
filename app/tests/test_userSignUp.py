'''
CS3250 - Software Development Methods and Tools - Project 3 Final
Team:SyntaxErrorz
Description: Project 3 User Task Management
'''

import unittest
from app import app, db
#from routes import users_signup

class UserSignUpTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_signup_route(self):
        response = self.app.post('/users_signup', data=dict(
            id='testuser',
            email='test@example.com',
            password='testpassword',
            password_confirm='testpassword'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__=='__main__':
    unittest.main()
