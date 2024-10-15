from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class YaNoteRouteTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="pass")
        self.user.save()

    def test_home_page_for_anonymous(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_note_pages_for_authenticated(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse("notes"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("done"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("add"))
        self.assertEqual(response.status_code, 200)

    def test_note_pages_for_unauthenticated(self):
        pages = ["notes", "done", "add"]
        for page in pages:
            response = self.client.get(reverse(page))
            self.assertRedirects(response, "/login/?next=" + reverse(page))

    def test_note_operations_for_non_author(self):
        other_user = User.objects.create_user(
            username="other", password="pass"
        )
        self.client.login(username="other", password="pass")
        response = self.client.get(reverse("note_detail", kwargs={"pk": 1}))
        self.assertEqual(response.status_code, 404)
