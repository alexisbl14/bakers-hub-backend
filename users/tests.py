from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status

# Create your tests here.
class UserAuthTests(TestCase):

    # set up testing client
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/users/register/'
        self.login_url = '/api/users/login/'
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123"
        }

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, "testuser")

    def test_login_user(self):
        # First register the user
        self.client.post(self.register_url, self.user_data, format='json')
        # Now test login
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)