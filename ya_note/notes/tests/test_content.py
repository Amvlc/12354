import pytest

from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from notes.models import Note
from notes.forms import NoteForm


@pytest.mark.django_db
def test_note_in_list_for_author(author_client):
    note = Note.objects.create(
        title="Заголовок", text="Текст заметки", author=author_client.user
    )
    url = reverse("notes:list")
    response = author_client.get(url)
    object_list = response.context["object_list"]

    assert note in object_list


@pytest.mark.django_db
def test_note_not_in_list_for_another_user(not_author_client):
    note = Note.objects.create(
        title="Заголовок", text="Текст заметки", author=not_author_client.user
    )
    another_user = User.objects.create(username="Другой пользователь")
    another_user_client = Client()
    another_user_client.force_login(another_user)

    url = reverse("notes:list")
    response = another_user_client.get(url)
    object_list = response.context["object_list"]

    assert note not in object_list


@pytest.mark.django_db
def test_create_note_page_contains_form(author_client):
    url = reverse("notes:add")
    response = author_client.get(url)

    assert "form" in response.context
    assert isinstance(response.context["form"], NoteForm)


@pytest.mark.django_db
def test_edit_note_page_contains_form(author_client):
    note = Note.objects.create(
        title="Заголовок", text="Текст заметки", author=author_client.user
    )
    url = reverse("notes:edit", args=(note.id,))
    response = author_client.get(url)

    assert "form" in response.context
    assert isinstance(response.context["form"], NoteForm)
