import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse
from news.models import Comment, News
from news.forms import WARNING


@pytest.fixture
def comment_data():
    return {"text": "Новый комментарий"}


@pytest.mark.django_db
def test_anonymous_user_cant_post_comment(client, comment_data):
    url = reverse("comments:post_comment", args=(1,))
    response = client.post(url, data=comment_data)
    login_url = reverse("users:login")
    expected_url = f"{login_url}?next={url}"
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_post_comment(author_client, comment_data):
    client, user = author_client
    news = News.objects.create(title="Тестовая новость", text="Содержимое")
    url = reverse("comments:post_comment", args=(news.id,))
    response = client.post(url, data=comment_data)

    assertRedirects(response, reverse("news:detail", args=(news.id,)))
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.first()
    assert new_comment.text == comment_data["text"]
    assert new_comment.author == user


@pytest.mark.django_db
def test_comment_with_prohibited_words(author_client, comment_data):
    comment_data["text"] = "Запрещенное слово"
    news = News.objects.create(title="Тестовая новость", text="Содержимое")
    url = reverse("comments:post_comment", args=(news.id,))
    response = author_client[0].post(url, data=comment_data)

    assertFormError(response, "form", "text", errors=(WARNING,))
    assert Comment.objects.count() == 0


@ pytest.mark.django_db
def test_author_can_edit_own_comment(author_client, comment_data):
    client, user = author_client
    news = News.objects.create(title="Тестовая новость", text="Содержимое")
    comment = Comment.objects.create(
        text="Старый комментарий", author=user, news=news)
    url = reverse("comments:edit", args=(comment.id,))

    comment_data["text"] = "Обновленный комментарий"
    response = client.post(url, data=comment_data)

    assertRedirects(response, reverse("news:detail", args=(news.id,)))
    comment.refresh_from_db()
    assert comment.text == comment_data["text"]


@ pytest.mark.django_db
def test_other_user_cant_edit_comment(not_author_client, comment_data):
    client, user = not_author_client
    news = News.objects.create(title="Тестовая новость", text="Содержимое")
    comment = Comment.objects.create(
        text="Комментарий другого пользователя", author=user, news=news)
    url = reverse("comments:edit", args=(comment.id,))

    response = client.post(url, data=comment_data)
    assert response.status_code == 404
    comment.refresh_from_db()
    assert comment.text == "Комментарий другого пользователя"


@ pytest.mark.django_db
def test_author_can_delete_own_comment(author_client):
    client, user = author_client
    news = News.objects.create(title="Тестовая новость", text="Содержимое")
    comment = Comment.objects.create(
        text="Комментарий для удаления", author=user, news=news)
    url = reverse("comments:delete", args=(comment.id,))

    response = client.post(url)
    assertRedirects(response, reverse("news:detail", args=(news.id,)))
    assert Comment.objects.count() == 0


@ pytest.mark.django_db
def test_other_user_cant_delete_comment(not_author_client):
    client, user = not_author_client
    news = News.objects.create(title="Тестовая новость", text="Содержимое")
    comment = Comment.objects.create(
        text="Комментарий другого пользователя", author=user, news=news)
    url = reverse("comments:delete", args=(comment.id,))

    response = client.post(url)
    assert response.status_code == 404
    assert Comment.objects.count() == 1
