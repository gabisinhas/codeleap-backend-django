from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ..models.post import Post

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

    def test_register(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)

    def test_login(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class PostTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', email='user1@email.com', password='pass1234')
        self.client = APIClient()
        login = self.client.post(reverse('login'), {'username': 'user1', 'password': 'pass1234'})
        self.token = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_post(self):
        url = reverse('createpost')
        data = {'title': 'Test Post', 'content': 'Some content'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], 'Test Post')

    def test_list_posts(self):
        Post.objects.create(username='user1', title='Post1', content='Content1')
        url = reverse('listposts')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_edit_post(self):
        post = Post.objects.create(username='user1', title='Old', content='Old content')
        url = reverse('editpost', args=[post.id])
        data = {'title': 'New', 'content': 'New content'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New')

    def test_delete_post(self):
        post = Post.objects.create(username='user1', title='To delete', content='Delete me')
        url = reverse('deletepost', args=[post.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_edit_post_forbidden(self):
        other = User.objects.create_user(username='user2', email='user2@email.com', password='pass5678')
        post = Post.objects.create(username='user2', title='Other', content='Other content')
        url = reverse('editpost', args=[post.id])
        data = {'title': 'Hack'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_post_forbidden(self):
        other = User.objects.create_user(username='user2', email='user2@email.com', password='pass5678')
        post = Post.objects.create(username='user2', title='Other', content='Other content')
        url = reverse('deletepost', args=[post.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
