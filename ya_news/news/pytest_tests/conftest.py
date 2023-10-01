import pytest
from news.models import News


@pytest.fixture
def news():
    return News.objects.create(
        title='Headline',
        text='Some news text.',
    )


@pytest.fixture
def news_id(news):
    return news.pk,
