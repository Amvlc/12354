import pytest

from http import HTTPStatus
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from notes.models import Note
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_home_page_accessibility_for_anonymous_user(client):
    url = reverse("notes:home")
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_authenticated_user_access_to_note_pages(author_client):
    url_list = [
        reverse("notes:list"),
        reverse("notes:add"),
        reverse("notes:success"),
    ]
    for url in url_list:
        response = author_client.get(url)
        assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_note_detail_edit_delete_accessibility_for_author(author_client):
    note = Note.objects.create(
        title="Заголовок", text="Текст", author=author_client.user
    )

    detail_url = reverse("notes:detail", args=(note.id,))
    edit_url = reverse("notes:edit", args=(note.id,))
    delete_url = reverse("notes:delete", args=(note.id,))

    assert author_client.get(detail_url).status_code == HTTPStatus.OK
    assert author_client.get(edit_url).status_code == HTTPStatus.OK
    assert author_client.get(delete_url).status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_anonymous_user_redirect_on_protected_note_pages(client):
    note = Note.objects.create(title="Заголовок", text="Текст")

    urls = [
        reverse("notes:edit", args=(note.id,)),
        reverse("notes:delete", args=(note.id,)),
        reverse("notes:detail", args=(note.id,)),
    ]

    login_url = reverse("users:login")

    for url in urls:
        response = client.get(url)
        expected_redirect_url = f"{login_url}?next={url}"
        assertRedirects(response, expected_redirect_url)


@pytest.mark.parametrize(
    "name", ("users:login", "users:logout", "users:signup")
)
@pytest.mark.django_db
def test_auth_pages_accessibility_for_anonymous_user(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
