from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note


class YaNoteContentTests(TestCase):
    LIST_URL = reverse("notes:list")
    CREATE_URL = reverse("notes:create")
    UPDATE_URL = reverse("notes:update", args=[1])

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="user", password="pass")
        cls.note = Note.objects.create(
            title="Test Note", text="This is a test.", author=cls.user
        )
        cls.other_user = User.objects.create_user(
            username="other", password="pass"
        )
        cls.other_note = Note.objects.create(
            title="Other Note",
            text="This is another test.",
            author=cls.other_user,
        )

    def setUp(self):
        self.client_user = self.client.force_login(self.user)
        self.client_other_user = self.client.force_login(self.other_user)

    def test_notes_list_context(self):
        response = self.client_user.get(self.LIST_URL)
        self.assertIn("object_list", response.context)
        self.assertIn(self.note, response.context["object_list"])

    def test_isolation_of_notes(self):
        response = self.client_user.get(self.LIST_URL)
        self.assertNotIn(self.other_note, response.context["object_list"])

    def test_create_note_form(self):
        response = self.client_user.get(self.CREATE_URL)
        self.assertIn("form", response.context)

    def test_update_note_form(self):
        response = self.client_user.get(self.UPDATE_URL)
        self.assertIn("form", response.context)
