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

    def test_page_accessibility(self):
        urls = {
            "home": reverse("notes:home"),
            "note_list": reverse("notes:list"),
            "note_detail": reverse(
                "notes:detail", kwargs={"slug": self.note.slug}
            ),
            "note_edit": reverse(
                "notes:edit", kwargs={"slug": self.note.slug}
            ),
            "note_delete": reverse(
                "notes:delete", kwargs={"slug": self.note.slug}
            ),
        }

        response = self.client.get(urls["home"])
        self.assertEqual(response.status_code, 200)

        for url_name in [
            "note_list",
            "note_detail",
            "note_edit",
            "note_delete",
        ]:
            with self.subTest(url=url_name):
                response = self.client.get(urls[url_name])
                self.assertRedirects(
                    response, f"/auth/login/?next={urls[url_name]}"
                )

        self.client.login(username="user", password="pass")
        for url_name in ["note_list", "note_detail", "note_edit"]:
            with self.subTest(url=url_name):
                response = self.client.get(urls[url_name])
                self.assertEqual(response.status_code, 200)

        self.client.login(username="other", password="pass")
        response = self.client.get(urls["note_edit"])
        self.assertEqual(response.status_code, 404)

        self.client.login(username="user", password="pass")
        response = self.client.get(urls["note_edit"])
        self.assertEqual(response.status_code, 200)
