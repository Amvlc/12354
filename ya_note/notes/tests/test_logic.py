from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note
from pytils.translit import slugify


class NotesViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.client.login(username="user", password="pass")

    def test_anonymous_user_cannot_create_note(self):
        self.client.logout()
        response = self.client.post(
            reverse("notes:create"),
            {"title": "Test Note", "text": "Test text"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(title="Test Note").exists())

    def test_slug_uniqueness(self):
        Note.objects.create(
            title="First Note",
            text="First text",
            author=self.user,
            slug="unique-slug",
        )
        response = self.client.post(
            reverse("notes:create"),
            {
                "title": "Second Note",
                "text": "Second text",
                "slug": "unique-slug",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "slug with this slug already exists.")

    def test_slug_auto_generation(self):
        response = self.client.post(
            reverse("notes:create"),
            {"title": "Auto Slug Note", "text": "Test text"},
        )
        note = Note.objects.get(id=response.context["object"].id)
        self.assertEqual(note.slug, slugify("Auto Slug Note"))

    def test_user_can_edit_own_note(self):
        note = Note.objects.create(
            title="Editable Note", text="Editable text", author=self.user
        )
        response = self.client.post(
            reverse("notes:update", args=[note.slug]),
            {"title": "Updated Note", "text": "Updated text"},
        )
        self.assertEqual(response.status_code, 302)
        note.refresh_from_db()
        self.assertEqual(note.title, "Updated Note")

    def test_user_cannot_edit_other_user_note(self):
        other_user = User.objects.create_user(
            username="other", password="pass"
        )
        note = Note.objects.create(
            title="Other User Note", text="Other text", author=other_user
        )
        response = self.client.post(
            reverse("notes:update", args=[note.slug]),
            {"title": "Malicious Edit", "text": "Malicious text"},
        )
        self.assertEqual(response.status_code, 403)

    def test_user_can_delete_own_note(self):
        note = Note.objects.create(
            title="Deletable Note", text="Deletable text", author=self.user
        )
        response = self.client.post(reverse("notes:delete", args=[note.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(id=note.id).exists())

    def test_user_cannot_delete_other_user_note(self):
        other_user = User.objects.create_user(
            username="other", password="pass"
        )
        note = Note.objects.create(
            title="Other User Note", text="Other text", author=other_user
        )
        response = self.client.post(reverse("notes:delete", args=[note.slug]))
        self.assertEqual(response.status_code, 403)
