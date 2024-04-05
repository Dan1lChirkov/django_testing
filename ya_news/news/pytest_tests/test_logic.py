import pytest

from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    assert Comment.objects.count() == 0
    url = reverse('news:detail', args=(news.pk,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, form_data, news):
    assert Comment.objects.count() == 0
    url = reverse('news:detail', args=(news.pk,))
    author_client.post(url, data=form_data)
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, form_data, comment):
    url = reverse('news:edit', args=(comment.pk,))
    author_client.post(url, data=form_data)
    comm = Comment.objects.get(pk=comment.pk)
    assert comm.text == form_data['text']


def test_author_can_delete_comment(author_client, comment):
    assert Comment.objects.count() == 1
    url = reverse('news:delete', args=(comment.pk,))
    author_client.post(url)
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_comment(not_author_client, form_data, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text


def test_other_user_cant_delete_comment(not_author_client, comment):
    assert Comment.objects.count() == 1
    url = reverse('news:delete', args=(comment.pk,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_if_bad_words_in_comment(author_client, news, form_data):
    assert Comment.objects.count() == 0
    url = reverse('news:detail', args=(news.pk,))
    form_data['text'] = 'негодяй'
    response = author_client.post(url, data=form_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0
