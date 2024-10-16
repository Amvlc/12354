import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from news.models import News, Comment


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="user", password="pass")


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(client):
    url = reverse("news:post_comment", kwargs={"news_id": 1})
    response = client.post(url, {"text": "Test comment"})
    assert response.status_code == 403


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(client, user):
    client.force_login(user)
    news = News.objects.create(title="Test News", text="Just testing")
    url = reverse("news:post_comment", kwargs={"news_id": news.id})
    response = client.post(url, {"text": "Test comment"})
    assert response.status_code == 302


@pytest.mark.django_db
def test_prevent_comment_with_forbidden_words(client, user):
    forbidden_words = ["badword"]
    client.force_login(user)
    news = News.objects.create(title="Sensitive News", text="Handle with care")
    url = reverse("news:post_comment", kwargs={"news_id": news.id})
    response = client.post(
        url, {"text": f"This contains a {forbidden_words[0]}"}
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_comment_edit_access_for_author(client, user):
    client.force_login(user)
    news = News.objects.create(title="News for Comment", text="Details")
    comment = Comment.objects.create(
        news=news, text="First comment", author=user
    )
    url = reverse("news:edit", kwargs={"pk": comment.pk})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_comment_edit_access_denied_for_non_author(client, user):
    another_user = User.objects.create_user("other", "pass")
    client.force_login(another_user)
    news = News.objects.create(title="News for Comment", text="Details")
    comment = Comment.objects.create(
        news=news, text="First comment", author=user
    )
    url = reverse("news:edit", kwargs={"pk": comment.pk})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_comment_edit_redirect_if_anonymous(client):
    url = reverse("news:edit", kwargs={"pk": 1})
    response = client.get(url)
    assert response.status_code == 302
