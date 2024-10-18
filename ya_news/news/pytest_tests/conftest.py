import pytest

from django.contrib.auth import get_user_model
from django.test import Client

from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def author_client(db):
    user = User.objects.create_user(username='author', password='password')
    client = Client()
    client.force_login(user)
    return client, user


@pytest.fixture
def not_author_client(db):
    user = User.objects.create_user(username="not_author", password="testpass")
    client = Client()
    client.login(username=user.username, password="testpass")
    return client


@pytest.fixture
def comment_data():
    return {"text": "Новый комментарий"}


@pytest.fixture
def news_item(author_client):
    return News.objects.create(
        title="Новость",
        text="Содержимое",
    )


@pytest.fixture
def comment_item(news_item, author_client):
    return Comment.objects.create(
        text="Комментарий",
        news=news_item,
        author=author_client[1],
    )
