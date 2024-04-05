from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class SetUpData(TestCase):

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
