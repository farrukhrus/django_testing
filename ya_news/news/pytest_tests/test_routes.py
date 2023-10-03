from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest import lazy_fixture
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:home', None),
        ('news:detail', lazy_fixture('news_id')),
        ('users:signup', None),
        ('users:login', None),
        ('users:logout', None),
    )
)
@pytest.mark.django_db
def test_page_availability_for_anonymous_client(client, name, news_object):
    """
    Доступность страниц анонимному пользователю.
    """
    response = client.get(reverse(name, args=news_object))
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('author_client'), HTTPStatus.OK),
        (lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:edit', lazy_fixture('comment_id')),
        ('news:delete', lazy_fixture('comment_id')),
    )
)
def test_availability_to_edit_delete_comment_by_auth_user(
    parametrized_client,
    expected_status,
    name,
    news_object,
):
    """
    Страницы удаления и редактирования комментария доступны автору комментария.
    """
    name = reverse(name, args=news_object)
    response = parametrized_client.get(name)
    assert (response.status_code == expected_status)


@pytest.mark.parametrize(
    'name, news_object',
    (
        ('news:edit', lazy_fixture('comment_id')),
        ('news:delete', lazy_fixture('comment_id')),
    )
)
def test_access_to_edit_delete_comment_by_anon(
    client,
    name,
    news_object,
):
    """
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    name = reverse(name, args=news_object)
    login_url = reverse('users:login')
    response = client.get(name)
    expected_url = f'{login_url}?next={name}'
    assertRedirects(response, expected_url)
