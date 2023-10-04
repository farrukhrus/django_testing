from django.urls import reverse
import pytest
from pytest import lazy_fixture

NEWS_COUNT = 10


@pytest.mark.django_db
@pytest.mark.usefixtures('news_list')
def test_news_count(client):
    """
    Количество новостей на главной странице — не более 10.
    """
    url = reverse('news:home')
    response = client.get(url)
    news_count = len(response.context['object_list'])
    assert news_count <= NEWS_COUNT


@pytest.mark.django_db
@pytest.mark.usefixtures('news_list')
def test_news_order(client):
    """
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    """
    url = reverse('news:home')
    response = client.get(url)
    news_dates = [news.date for news in response.context['object_list']]
    ordered_dates = sorted(news_dates, reverse=True)
    assert news_dates == ordered_dates


@pytest.mark.usefixtures('comments_list')
def test_comments_order(client, news_id):
    """
    Комментарии на странице отдельной новости отсортированы
    в хронологическом порядке: старые в начале списка, новые — в конце.

    """
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    all_comments = response.context['news'].comment_set.all()
    assert list(all_comments) == list(all_comments.order_by('created'))


@pytest.mark.parametrize(
    'parametrized_client, form_is_shown',
    (
        (lazy_fixture('author_client'), True),
        (lazy_fixture('client'), False),
    )
)
@pytest.mark.django_db
def test_form_is_shown_to_correct_user(
    parametrized_client,
    form_is_shown,
    news_id,
):
    """
    Анонимному пользователю недоступна форма для отправки комментария
    на странице отдельной новости, а авторизованному доступна.
    """
    url = reverse('news:detail', args=news_id)
    response = parametrized_client.get(url)
    assert ('form' in response.context) == form_is_shown
