from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AdminAuthenticationTests(APITestCase):
    def test_django_superuser_receives_admin_role(self):
        user_model = get_user_model()
        user_model.objects.create_superuser(
            username='django-superuser',
            email='superuser@example.com',
            password='Strong-pass-123!',
        )
        response = self.client.post(
            reverse('accounts:token_obtain_pair'),
            {'username': 'django-superuser', 'password': 'Strong-pass-123!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'admin')
