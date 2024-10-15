import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture
def client():
    return Client()


def test_home_page_accessibility(client):
    url = reverse("notes:home")
    response = client.get(url)
    assert response.status_code == 200


def test_note_detail_accessibility(client):
    url = reverse("notes:detail", kwargs={"pk": 1})
    response = client.get(url)
    assert response.status_code == 200


def test_note_edit_access_for_author(client):
    user = User.objects.create_user(username="author", password="pass")
    client.force_login(user)
    url = reverse("notes:edit", kwargs={"pk": 1})
    response = client.get(url)
    assert response.status_code == 200


def test_note_edit_redirect_if_anonymous(client):
    url = reverse("notes:edit", kwargs={"pk": 1})
    response = client.get(url)
    assert response.status_code == 302


def test_note_edit_access_denied_for_non_author(client):
    another_user = User.objects.create_user("other", "pass")
    client.force_login(another_user)
    url = reverse("notes:edit", kwargs={"pk": 1})
    response = client.get(url)
    assert response.status_code == 404
