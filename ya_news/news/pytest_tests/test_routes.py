import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    user = User.objects.create_user(username="user", password="pass")
    return user


def test_home_page_accessibility(client):
    url = reverse("news:home")
    response = client.get(url)
    assert response.status_code == 200


def test_news_detail_accessibility(client):
    url = reverse("news:detail", kwargs={"pk": 1})
    response = client.get(url)
    assert response.status_code == 200


def test_comment_edit_access_for_author(client, user):
    client.force_login(user)
    url = reverse("news:edit", kwargs={"pk": 1})
    response = client.get(url)
    assert response.status_code == 200


def test_comment_edit_redirect_if_anonymous(client):
    url = reverse("news:edit", kwargs={"pk": 1})
    response = client.get(url)
    assert response.status_code == 302
    assert "/login/" in response.url


def test_comment_edit_access_denied_for_non_author(client, user):
    other_user = User.objects.create_user("other", "pass")
    client.force_login(other_user)
    url = reverse("news:edit", kwargs={"pk": 1})
    response = client.get(url)
    assert response.status_code == 404
