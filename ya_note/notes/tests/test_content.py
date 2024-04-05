from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.forms import NoteForm
from notes.tests.common import SetUpData

User = get_user_model()


class TestContent(SetUpData):

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
