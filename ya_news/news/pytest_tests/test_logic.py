from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest import lazy_fixture
from pytest_django.asserts import assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


@pytest.mark.parametrize(
    'parametrized_client, expected_count',
    (
        (lazy_fixture('author_client'), 1),
        (lazy_fixture('client'), 0),
    )
)
@pytest.mark.django_db
def test_add_comment(
    parametrized_client,
    expected_count,
    news_id,
    form_data,
):
    """
    Анонимный пользователь не может отправить комментарий.
    Авторизованный пользователь может отправить комментарий.
    """
    url = reverse('news:detail', args=news_id)
    parametrized_client.post(url, data=form_data)
    assert (Comment.objects.count() == expected_count)


def test_no_bad_words(author_client, news_id):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=news_id)
    response = author_client.post(url, data={'text': BAD_WORDS[0]})
    assertFormError(
        response,
        'form',
        'text',
        WARNING,
    )
    assert (Comment.objects.count() == 0)


@pytest.mark.parametrize(
    'parametrized_client, expected_count',
    (
        (lazy_fixture('author_client'), 0),
        (lazy_fixture('admin_client'), 1),
    )
)
def test_can_delete_comment(
    parametrized_client,
    expected_count,
    comment_id,
):
    """
    Авторизованный пользователь может удалять свои комментарии.
    Авторизованный пользователь не может удалять чужие комментарии.
    """
    url = reverse('news:delete', args=comment_id)
    parametrized_client.post(url)
    comments_count = Comment.objects.count()
    assert (comments_count == expected_count)


@pytest.mark.parametrize(
    'parametrized_client, expected_text, expected_status',
    (
        (
            lazy_fixture('admin_client'), 0, HTTPStatus.NOT_FOUND,
        ),
        (
            lazy_fixture('author_client'), 1, HTTPStatus.FOUND,
        ),
    )
)
def test_edit_comment(
    parametrized_client,
    expected_text,
    expected_status,
    comment_id,
    form_data,
    comment_text,
):
    """
    Авторизованный пользователь может редактировать свои комментарии.
    Авторизованный пользователь не может редактировать чужие комментарии.
    """
    url = reverse('news:edit', args=comment_id)
    response = parametrized_client.post(url, data=form_data)
    assert (response.status_code == expected_status)
    edited_comment = Comment.objects.get()
    assert (edited_comment.text == comment_text[expected_text])
