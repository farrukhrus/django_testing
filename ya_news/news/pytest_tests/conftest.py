from datetime import datetime, timedelta
from time import sleep

import pytest

from news.models import News, Comment

NEWS_COUNT = 10


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Новый текст.',
    )


@pytest.fixture
def news_id(news):
    return news.pk,


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(
        username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def comment_text():
    return (
        'Текст',
        'Новый текст',
    )


@pytest.fixture
def comment(author, news, comment_text):
    return Comment.objects.create(
        news=news,
        author=author,
        text=comment_text[0],
    )


@pytest.fixture
def comment_id(comment):
    return comment.pk,


@pytest.fixture
def form_data(comment_text):
    return {'text': comment_text[1]}


@pytest.fixture
def news_list():
    news = []
    today = datetime.today()
    for index in range(NEWS_COUNT + 1):
        news_piece = News.objects.create(
            title=f'Новость {index}',
            text=f'Текст {index}.',
            date=today - timedelta(days=index),
        )
        news.append(news_piece)
    return news


@pytest.fixture
def comments_list(author, news):
    now = datetime.now()
    comments = []
    for index in range(2):
        # для корректной работы теста test_comments_order
        sleep(0.1)
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}.',
            created=now + timedelta(hours=index)
        )
        comments.append(comment)
    return comments
