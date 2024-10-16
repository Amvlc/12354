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


@pytest.fixture
def setup_news(db):
    news_list = [
        News.objects.create(title=f"News {i}", text="Some text for News {i}")
        for i in range(15)
    ]
    return news_list


@pytest.mark.django_db
def test_news_count_and_order(client, setup_news):
    url = reverse("news:home")
    response = client.get(url)
    assert len(response.context["object_list"]) == 10
    assert response.context["object_list"][0].title == "News 0"


@pytest.mark.django_db
def test_comments_order_in_news_detail(client, db):
    news = News.objects.create(title="News for Comment", text="Details")
    c1 = Comment.objects.create(
        news=news,
        text="First comment",
        author=User.objects.create_user("firstuser", "pass"),
    )
    c2 = Comment.objects.create(
        news=news,
        text="Second comment",
        author=User.objects.create_user("seconduser", "pass"),
    )
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = client.get(url)
    comments = response.context["news"].comment_set.all()
    assert comments[0] == c1
    assert comments[1] == c2
