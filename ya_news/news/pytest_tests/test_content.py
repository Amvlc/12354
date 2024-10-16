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


@pytest.mark.django_db
def test_home_page_accessibility(client):
    url = reverse("news:home")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_news_detail_accessibility(client):
    news = News.objects.create(title="News", text="Details")
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(client, setup_news):
    news = setup_news[0]
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = client.post(url, {"text": "Test comment"})
    assert response.status_code == 302


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(client, user, setup_news):
    client.force_login(user)
    news = setup_news[0]
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = client.post(url, {"text": "Test comment"})
    assert response.status_code == 302


@pytest.mark.django_db
def test_prevent_comment_with_forbidden_words(client, user, setup_news):
    client.force_login(user)
    news = setup_news[0]
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = client.post(url, {"text": "This contains a badword"})
    assert response.status_code == 200
    assert not Comment.objects.filter(text="This contains a badword").exists()
