from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.apps import apps

Note = apps.get_model("notes", "Note")


class YaNoteContentTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.note = Note.objects.create(
            title="Test Note", text="This is a test.", author=self.user
        )

    def test_notes_list_context(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse("notes:list"))
        self.assertIn("object_list", response.context)
        self.assertIn(self.note, response.context["object_list"])

    def test_isolation_of_notes(self):
        other_user = User.objects.create_user(
            username="other", password="pass"
        )
        other_note = Note.objects.create(
            title="Other Note",
            text="This is another test.",
            author=other_user,
        )
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse("notes:list"))
        self.assertNotIn(other_note, response.context["object_list"])
