from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ContactMessage


class ContactMessagePermissionTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(
            username='contact-admin', password='Strong-pass-123!', role='admin'
        )
        self.user = user_model.objects.create_user(
            username='contact-user', password='Strong-pass-123!', role='user'
        )
        self.message = ContactMessage.objects.create(
            full_name='Test User', email='test@example.com', phone='+998901234567',
            subject='general', message='Bu yetarlicha uzun test xabari.',
        )

    def test_regular_user_cannot_read_personal_messages(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(reverse('contact:contact-list'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        response = self.client.get(
            reverse('contact:contact-detail', kwargs={'pk': self.message.pk})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_read_messages(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('contact:contact-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
