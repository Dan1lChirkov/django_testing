from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class Testlogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.author = User.objects.create(username='Гриша')
        cls.reader = User.objects.create(username='Данил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.reader)
        cls.second_auth_client = Client()
        cls.second_auth_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': '1',
        }

    def test_user_can_create_note(self):
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.reader)

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        redirect_url = f'{login_url}?next={self.url}'
        self.assertRedirects(response, redirect_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_empty_slug(self):
        self.form_data.pop('slug')
        response = self.second_auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestNoteEditDeleteAndNotUniqueSlug(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Гриша')
        cls.reader = User.objects.create(username='Данил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.reader)
        cls.second_auth_client = Client()
        cls.second_auth_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', slug='1', author=cls.author
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.success_url = reverse('notes:success')
        cls.edit_form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': '2',
        }

    def test_author_can_edit_note(self):
        response = self.second_auth_client.post(
            self.edit_url, data=self.edit_form_data
        )
        self.assertRedirects(response, self.success_url)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.edit_form_data['title'])
        self.assertEqual(self.note.text, self.edit_form_data['text'])
        self.assertEqual(self.note.slug, self.edit_form_data['slug'])

    def test_author_can_delete_note(self):
        response = self.second_auth_client.post(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_edit_note(self):
        response = self.auth_client.post(self.edit_url, self.edit_form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_form_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_form_db.title)
        self.assertEqual(self.note.text, note_form_db.text)
        self.assertEqual(self.note.slug, note_form_db.slug)

    def test_other_user_cant_delete_note(self):
        response = self.auth_client.post(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_not_unique_slug(self):
        self.edit_form_data['slug'] = self.note.slug
        response = self.second_auth_client.post(
            self.add_url, data=self.edit_form_data
        )
        self.assertFormError(
            response, 'form', 'slug', errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)
