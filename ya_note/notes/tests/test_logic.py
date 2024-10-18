import pytest

from django.urls import reverse
from django.test import Client
from notes.models import Note
from django.contrib.auth import get_user_model
from pytils.translit import slugify

User = get_user_model()


@pytest.mark.django_db
class TestNoteCreationAndEditing:
    @pytest.fixture
    def author_client(self, django_user_model):
        user = django_user_model.objects.create_user(
            username="Автор", password="password"
        )
        client = Client()
        client.login(username="Автор", password="password")
        return client, user

    @pytest.fixture
    def anonymous_client(self):
        return Client()

    def test_authenticated_user_can_create_note(self, author_client):
        client, user = author_client
        url = reverse("notes:add")
        data = {"title": "Заголовок", "text": "Текст заметки"}
        response = client.post(url, data=data)

        assert response.status_code == 302
        assert Note.objects.count() == 1
        note = Note.objects.first()
        assert note.author == user

    def test_anonymous_user_cannot_create_note(self, anonymous_client):
        url = reverse("notes:add")
        data = {"title": "Заголовок", "text": "Текст заметки"}
        response = anonymous_client.post(url, data=data)

        assert response.status_code == 302
        assert Note.objects.count() == 0

    def test_slug_uniqueness(self, author_client):
        client, user = author_client
        url = reverse("notes:add")

        data1 = {
            "title": "Заголовок 1",
            "text": "Текст заметки 1",
            "slug": "unique-slug",
        }
        client.post(url, data=data1)

        data2 = {
            "title": "Заголовок 2",
            "text": "Текст заметки 2",
            "slug": "unique-slug",
        }
        response = client.post(url, data=data2)

        assert response.status_code == 200
        assert Note.objects.count() == 1

    def test_slug_auto_generation(self, author_client):
        client, user = author_client
        url = reverse("notes:add")

        data = {"title": "Заголовок без slug", "text": "Текст заметки"}
        response = client.post(url, data=data)

        assert response.status_code == 302
        note = Note.objects.first()
        assert note.slug == slugify("Заголовок без slug")

    def test_author_can_edit_own_note(self, author_client):
        client, user = author_client
        note = Note.objects.create(
            title="Заголовок", text="Текст заметки", author=user
        )
        url = reverse("notes:edit", args=[note.id])

        data = {"title": "Обновленный заголовок", "text": "Обновленный текст"}
        response = client.post(url, data=data)

        assert response.status_code == 302
        note.refresh_from_db()
        assert note.title == "Обновленный заголовок"
        assert note.text == "Обновленный текст"

    def test_author_cannot_edit_another_users_note(self, author_client):
        client, user = author_client
        another_user = User.objects.create(
            username="Другой Автор", password="password"
        )
        note = Note.objects.create(
            title="Заголовок", text="Текст заметки", author=another_user
        )
        url = reverse("notes:edit", args=[note.id])

        data = {
            "title": "Попытка редактирования",
            "text": "Текст не должен измениться",
        }
        response = client.post(url, data=data)

        assert response.status_code == 404
        note.refresh_from_db()
        assert note.title == "Заголовок"
        assert note.text == "Текст заметки"

    def test_author_can_delete_own_note(self, author_client):
        client, user = author_client
        note = Note.objects.create(
            title="Заголовок", text="Текст заметки", author=user
        )
        url = reverse("notes:delete", args=[note.id])

        response = client.delete(url)

        assert response.status_code == 302
        assert Note.objects.count() == 0

    def test_author_cannot_delete_another_users_note(self, author_client):
        client, user = author_client
        another_user = User.objects.create(
            username="Другой Автор", password="password"
        )
        note = Note.objects.create(
            title="Заголовок", text="Текст заметки", author=another_user
        )
        url = reverse("notes:delete", args=[note.id])

        response = client.delete(url)

        assert response.status_code == 404
        assert Note.objects.count() == 1
