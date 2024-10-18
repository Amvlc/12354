import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from news.models import News, Comment

User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def setup_news(db):
    news_list = [
        News(title=f"News {i}", text=f"Some text for News {i}")
        for i in range(11)
    ]
    News.objects.bulk_create(news_list)
    return news_list


@pytest.fixture
def setup_comments(db, setup_news):
    news = setup_news[0]
    comments = [
        Comment(
            news=news,
            text=f"Comment {i}",
            author=User.objects.create_user(
                username=f"commenter{i}", password="pass"
            ),
        )
        for i in range(5)
    ]
    Comment.objects.bulk_create(comments)
    return comments


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="user", password="pass")


@pytest.fixture
def setup_news(db):
    news_list = [
        News.objects.create(title=f"News {i}", text="Some text for News {i}")
        for i in range(15)
    ]
    return news_list
