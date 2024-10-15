import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from news.models import News


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="user", password="pass")


def test_anonymous_user_cannot_post_comment(client):
    url = reverse("news:post_comment", kwargs={"pk": 1})
    client.post(url, {"content": "Test comment"})


def test_authenticated_user_can_post_comment(client, user):
    client.force_login(user)
    news = News.objects.create(title="Test News", content="Just testing")
    url = reverse("news:post_comment", kwargs={"pk": news.pk})
    client.post(url, {"content": "Test comment"})


def test_prevent_comment_with_forbidden_words(client, user):
    forbidden_words = ["badword"]
    client.force_login(user)
    news = News.objects.create(
        title="Sensitive News", content="Handle with care"
    )
    url = reverse("news:post_comment", kwargs={"pk": news.pk})
    client.post(url, {"content": f"This contains a {forbidden_words[0]}"})
