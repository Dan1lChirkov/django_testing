import pytest

from http import HTTPStatus
from pytest_django.asserts import assertRedirects
from django.urls import reverse

author = pytest.lazy_fixture('author_client')
not_author = pytest.lazy_fixture('not_author_client')
comment = pytest.lazy_fixture('comment')
news_id = pytest.lazy_fixture('id_for_news')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', news_id),
    ),
)
def test_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (author, HTTPStatus.OK),
        (not_author, HTTPStatus.NOT_FOUND)
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit'),
)
def test_pages_availability_for_different_users(
    parametrized_client, name, expected_status, comment
):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', comment),
        ('news:delete', comment),
    ),
)
def test_redirects(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=(args.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
