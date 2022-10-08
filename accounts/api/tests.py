from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

class AccountApiTests(TestCase):

    def setUp(self):
        # this function will be executed before every test fuction being executed
        self.client = APIClient()
        self.user = self.createUser(
            username='admin',
            email='admin@gmail.com',
            password='correct password',
        )

    def createUser(self, username, email, password):
        return User.objects.create_user(username, email, password)

    def test_login(self):
        # prefix with test_ will be used for test
        # need to use POST rather than GET to test
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # 405, method not allowed for GET
        self.assertEqual(response.status_code, 405)

        # use POST but wrong password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # check if we has_logged_in or not, should be no
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # use POST and correct passwords
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@gmail.com')

        # check if we has_logged_in or not, should be yes
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # login
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # check if we has_logged_in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # check if we are using POST rather than GET
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # use POST and logout
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        # check if we has_logged_in or not, should be no
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@gmail.com',
            'password': 'any password',
        }
        # should fail if we use GET for test
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # check with wrong email format
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not in email format',
            'password': 'any password'
        })
        self.assertEqual(response.status_code, 400)

        # check short password
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@gmail.com',
            'password': '123',
        })
        self.assertEqual(response.status_code, 400)

        # check long username
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@gmail.com',
            'password': 'any password',
        })
        self.assertEqual(response.status_code, 400)

        # successful signup
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')
        # check if the user has logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)