from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from ya_note.models import Note


class YaNoteLogicTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")

    def test_note_creation_by_authenticated_user(self):
        self.client.login(username="user", password="pass")
        response = self.client.post(
            reverse("add"),
            {"title": "New Note", "content": "Content of new note."},
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_note_creation_by_anonymous_user(self):
        response = self.client.post(
            reverse("add"),
            {"title": "New Note", "content": "Content of new note."},
        )
        self.assertEqual(Note.objects.count(), 0)
