


from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from core.models.post import Post

User = get_user_model()

class AuthTests(APITestCase):
	def setUp(self):
		self.register_url = reverse('register')
		self.login_url = reverse('login')
		self.user_data = {
			'username': 'testuser',
			'email': 'testuser@example.com',
			'password': 'testpass123'
		}




