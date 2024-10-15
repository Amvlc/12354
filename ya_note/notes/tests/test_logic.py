import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="user", password="pass")


def test_anonymous_user_cannot_create_note(client):
    url = reverse("notes:create")
    client.post(url, {"title": "New Note", "content": "Test content"})


def test_authenticated_user_can_create_note(client, user):
    client.force_login(user)
    url = reverse("notes:create")
    client.post(url, {"title": "New Note", "content": "Test content"})


def test_prevent_creation_with_forbidden_words(client, user):
    forbidden_words = ["forbidden"]
    client.force_login(user)
    url = reverse("notes:create")
    client.post(
        url,
        {
            "title": "Forbidden Note",
            "content": f"This contains a {forbidden_words[0]}",
        },
    )
