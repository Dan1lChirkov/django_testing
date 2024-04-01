import pytest

from django.test.client import Client
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta


from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Название',
        text='Текст',
    )
    return news


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )
    return comment


@pytest.fixture
def pk_comment(comment):
    return (comment.pk,)


@pytest.fixture
def add_news():
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(title=f'Новость {index}', text='Просто текст.',
                    date=today - timedelta(days=index))
        all_news.append(news)
    News.objects.bulk_create(all_news)
    return News


@pytest.fixture
def make_ten_comments(news, author):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return Comment


@pytest.fixture
def form_data():
    return {
        'text': 'Новый текст'
    }
