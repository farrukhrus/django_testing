from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest import lazy_fixture
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url, url_args',
    (
        ('news:home', None),
        ('news:detail', lazy_fixture('news_id')),
        ('users:signup', None),
        ('users:login', None),
        ('users:logout', None),
    )
)
@pytest.mark.django_db
def test_page_availability_for_anonymous_client(client, url, url_args):
    """
    доступность страниц анонимному пользователю
    """
    response = client.get(reverse(url, args=url_args))
    assert response.status_code == HTTPStatus.OK
