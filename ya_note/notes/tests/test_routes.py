from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.apps import apps

Note = apps.get_model("notes", "Note")


class YaNoteRoutesTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user", password="pass")
        self.note = Note.objects.create(
            title="Test Note", text="This is a test note", author=self.user
        )

    def test_home_page_accessibility(self):
        response = self.client.get(reverse("notes:home"))
        self.assertEqual(response.status_code, 200)

    def test_note_detail_accessibility(self):
        self.client.login(username="user", password="pass")
        url = reverse("notes:detail", kwargs={"slug": self.note.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_note_edit_access_denied_for_non_author(self):
        other_user = User.objects.create_user(
            username="other", password="pass"
        )
        self.client.login(username="other", password="pass")
        url = reverse("notes:edit", kwargs={"slug": self.note.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()
        self.client.login(username=other_user.username, password="pass")

    def test_note_edit_access_for_author(self):
        self.client.login(username="user", password="pass")
        url = reverse("notes:edit", kwargs={"slug": self.note.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_note_edit_redirect_if_anonymous(self):
        url = reverse("notes:edit", kwargs={"slug": self.note.slug})
        response = self.client.get(url)
        self.assertRedirects(response, f"/auth/login/?next={url}")

    def test_note_list_accessibility(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse("notes:list"))
        self.assertEqual(response.status_code, 200)
