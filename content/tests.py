from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Announcement, News


class PublicContentSecurityTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin = user_model.objects.create_user(
            username='admin-test', password='Strong-pass-123!', role='admin'
        )
        self.user = user_model.objects.create_user(
            username='user-test', password='Strong-pass-123!', role='user'
        )
        now = timezone.now()
        self.published = News.objects.create(
            title_uz='Ochiq yangilik', status=News.Status.PUBLISHED,
            published_at=now - timedelta(minutes=1), created_by=self.admin,
        )
        self.draft = News.objects.create(
            title_uz='Qoralama', status=News.Status.DRAFT, created_by=self.admin,
        )
        self.future = News.objects.create(
            title_uz='Kelajakdagi yangilik', status=News.Status.PUBLISHED,
            published_at=now + timedelta(days=1), created_by=self.admin,
        )
        self.active_announcement = Announcement.objects.create(
            title_uz='Faol e\'lon', status=Announcement.Status.PUBLISHED,
            published_at=now - timedelta(minutes=1),
            expires_at=now + timedelta(days=1), created_by=self.admin,
        )
        self.expired_announcement = Announcement.objects.create(
            title_uz='Eskirgan e\'lon', status=Announcement.Status.PUBLISHED,
            published_at=now - timedelta(days=2),
            expires_at=now - timedelta(days=1), created_by=self.admin,
        )

    def test_anonymous_list_hides_non_public_news(self):
        response = self.client.get(reverse('content:news-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = {item['slug'] for item in response.data['results']}
        self.assertEqual(slugs, {self.published.slug})

    def test_anonymous_detail_hides_draft_news(self):
        response = self.client.get(
            reverse('content:news-detail', kwargs={'slug': self.draft.slug})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_list_hides_expired_announcements(self):
        response = self.client.get(reverse('content:announcement-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = {item['slug'] for item in response.data['results']}
        self.assertEqual(slugs, {self.active_announcement.slug})

    def test_regular_user_cannot_create_content(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            reverse('content:news-list-create'),
            {'title_uz': 'Ruxsatsiz', 'status': News.Status.PUBLISHED},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_see_drafts_and_create_content(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(reverse('content:news-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        response = self.client.post(
            reverse('content:news-list-create'),
            {'title_uz': 'Admin yangiligi', 'status': News.Status.DRAFT},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
