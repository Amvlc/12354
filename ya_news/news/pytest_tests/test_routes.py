import pytest

from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from django.urls import reverse

from news.models import News, Comment


@pytest.mark.django_db
def test_home_page_accessibility_for_anonymous_user(client):
    url = reverse("news:home")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_detail_accessibility_for_anonymous_user(client, news_item):
    url = reverse("news:detail", args=(news_item.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_comment_edit_delete_accessibility_for_author(
    author_client, comment_item
):
    client, user = author_client
    edit_url = reverse("comments:edit", args=(comment_item.id,))
    delete_url = reverse("comments:delete", args=(comment_item.id,))

    edit_response = client.get(edit_url)
    delete_response = client.get(delete_url)

    assert edit_response.status_code == HTTPStatus.OK
    assert delete_response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_anonymous_user_redirect_on_comment_edit_delete(client, news_item):
    comment = Comment.objects.create(text="Комментарий", news=news_item)

    edit_url = reverse("comments:edit", args=(comment.id,))
    delete_url = reverse("comments:delete", args=(comment.id,))

    expected_redirect_url = reverse("users:login") + f"?next={edit_url}"

    edit_response = client.get(edit_url)
    delete_response = client.get(delete_url)

    assertRedirects(edit_response, expected_redirect_url)
    assertRedirects(delete_response, expected_redirect_url)


@pytest.mark.django_db
def test_authorized_user_cannot_access_others_comment_edit_delete(
    not_author_client,
):
    news = News.objects.create(
        title="Новость", text="Содержимое", author=not_author_client[1]
    )
    comment = Comment.objects.create(
        text="Комментарий другого пользователя",
        news=news,
        author=not_author_client[1],
    )

    edit_url = reverse("comments:edit", args=(comment.id,))
    delete_url = reverse("comments:delete", args=(comment.id,))

    response = not_author_client[0].get(edit_url)
    assert response.status_code == 404

    response = not_author_client[0].get(delete_url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_comment_creation_redirects_to_news_detail(
    author_client, comment_data
):
    client, user = author_client
    news = News.objects.create(title="Тестовая новость", text="Содержимое")
    url = reverse("comments:post_comment", args=(news.id,))

    response = client.post(url, data=comment_data)
    assertRedirects(response, reverse("news:detail", args=(news.id,)))


@pytest.mark.django_db
def test_comment_creation_with_invalid_data(author_client):
    client, user = author_client
    news = News.objects.create(title="Тестовая новость", text="Содержимое")
    url = reverse("comments:post_comment", args=(news.id,))

    invalid_data = {"text": ""}
    response = client.post(url, data=invalid_data)

    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors
