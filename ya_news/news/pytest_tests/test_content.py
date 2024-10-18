import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from http import HTTPStatus
from news.models import Comment


@pytest.mark.django_db
def test_news_count_and_order(client, setup_news):
    url = reverse("news:home")
    response = client.get(url)

    assert response.context["object_list"].count() == 10
    assert response.context["object_list"].first().title == "News 0"


@pytest.mark.django_db
def test_comments_order_in_news_detail(client, setup_comments):
    news = setup_comments[0].news
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = client.get(url)

    comments = response.context["news"].comment_set.all()

    assert comments.first().text == "Comment 0"
    assert comments.last().text == "Comment 4"


@pytest.mark.django_db
def test_comment_edit_access_for_author(authenticated_client, setup_comments):
    comment = setup_comments[0]
    assert comment.pk is not None
    url = reverse("news:edit", kwargs={"pk": comment.pk})
    response = authenticated_client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comment_edit_access_denied_for_non_author(client, setup_comments):
    another_user = User.objects.create_user("otheruser", "pass")
    client.force_login(another_user)
    comment = setup_comments[0]
    url = reverse("news:edit", kwargs={"pk": comment.pk})
    response = client.get(url)

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_comment_edit_redirect_if_anonymous(client):
    url = reverse("news:edit", kwargs={"pk": 1})
    response = client.get(url)

    assert response.status_code == HTTPStatus.FOUND
    assert response.url.startswith(reverse("users:login"))


@pytest.mark.django_db
def test_home_page_accessibility(client):
    url = reverse("news:home")
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_accessibility(client, setup_news):
    news = setup_news[0]
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = client.get(url)

    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_anonymous_user_cannot_post_comment(client, setup_news):
    news = setup_news[0]
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = client.post(url, {"text": "Test comment"})

    assert response.status_code == HTTPStatus.FOUND


@pytest.mark.django_db
def test_authenticated_user_can_post_comment(authenticated_client, setup_news):
    news = setup_news[0]
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = authenticated_client.post(url, {"text": "Test comment"})

    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.filter(text="Test comment").exists()


@pytest.mark.django_db
def test_prevent_comment_with_forbidden_words(
    authenticated_client, setup_news
):
    news = setup_news[0]
    url = reverse("news:detail", kwargs={"pk": news.pk})
    response = authenticated_client.post(
        url, {"text": "This contains a badword"}
    )

    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(text__contains="badword").exists()
