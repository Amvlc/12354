import pytest

from django.urls import reverse
from django.utils import timezone

from news.models import News, Comment
from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count_on_home_page(author_client):
    client, user = author_client
    for i in range(15):
        News.objects.create(
            title=f"Новость {i}",
            text="Содержимое новости",
        )

    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context["object_list"]

    assert len(object_list) <= 10


@pytest.mark.django_db
def test_news_sorted_by_date(author_client):
    client, user = author_client
    news1 = News.objects.create(title="Старая новость", text="Содержимое")
    news2 = News.objects.create(title="Свежая новость", text="Содержимое")

    news1.date = timezone.datetime(2023, 1, 1)
    news2.date = timezone.datetime(2023, 1, 2)
    news1.save()
    news2.save()

    url = reverse("news:home")
    response = client.get(url)
    object_list = response.context["object_list"]

    assert object_list[0] == news2
    assert object_list[1] == news1


@pytest.mark.django_db
def test_comments_sorted_by_date(author_client):
    client, user = author_client
    news = News.objects.create(title="Новость", text="Содержимое")
    comment1 = Comment.objects.create(
        text="Старый комментарий", news=news, author=user)
    comment2 = Comment.objects.create(
        text="Новый комментарий", news=news, author=user)

    comment1.created = timezone.datetime(2023, 1, 1)
    comment2.created = timezone.datetime(2023, 1, 2)
    comment1.save()
    comment2.save()

    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)
    comments_list = response.context["comments"]

    assert comments_list[0] == comment2
    assert comments_list[1] == comment1


@pytest.mark.django_db
def test_anonymous_user_cannot_access_comment_form(client):
    news = News.objects.create(title="Новость", text="Содержимое")
    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)

    assert "form" not in response.context


@pytest.mark.django_db
def test_authorized_user_can_access_comment_form(author_client):
    client, user = author_client
    news = News.objects.create(title="Новость", text="Содержимое")
    url = reverse("news:detail", args=(news.id,))
    response = client.get(url)

    assert "form" in response.context
    assert isinstance(response.context["form"], CommentForm)
