import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from news.models import News, Comment


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def setup_news(db):
    user = User.objects.create_user("user", "pass")
    news_list = [
        News.objects.create(title=f"News {i}", content="Content")
        for i in range(15)
    ]
    return news_list


def test_news_count_and_order(client, setup_news):
    url = reverse("news:home")
    response = client.get(url)
    assert len(response.context["object_list"]) <= 10
    assert response.context["object_list"][0].title == "News 14"


def test_comments_order_in_news_detail(client):
    news = News.objects.create(title="News for Comment", content="Details")
    c1 = Comment.objects.create(
        news=news,
        content="First comment",
        author=User.objects.create_user("firstuser", "pass"),
    )
    c2 = Comment.objects.create(
        news=news,
        content="Second comment",
        author=User.objects.create_user("seconduser", "pass"),
    )
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = client.get(url)
    assert response.context["comment_set"][0] == c1
    assert response.context["comment_set"][1] == c2
