from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Гриша')
        cls.reader = User.objects.create(username='Данил')
        cls.note = Note.objects.create(
            title='Заголовок', text='Текст', slug='1', author=cls.author
        )

    def test_notes_list_for_different_users(self):
        users_list = (
            (self.author, True),
            (self.reader, False),
        )
        for user, note_in_list in users_list:
            self.client.force_login(user)
            with self.subTest(user=user):
                url = reverse('notes:list')
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual((self.note in object_list), note_in_list)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        self.client.force_login(self.author)
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
