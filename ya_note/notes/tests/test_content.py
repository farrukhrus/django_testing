from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class Tests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Headline',
            text='Some text.',
            author=cls.author,
            slug='slug',
        )

        cls.url_list = reverse('notes:list')
        cls.url_add = reverse('notes:add')
        cls.url_edit = reverse('notes:edit', args=(cls.note.slug,))

    def test_notes_list(self):
        """
        в список заметок одного пользователя
        не попадают заметки другого пользователя
        """
        test_cases = (
            (self.author_client, 1),
            (self.reader_client, 0),
        )
        for client, expected_outcome in test_cases:
            with self.subTest(client):
                response = client.get(self.url_list)
                object_list = response.context['object_list']
                self.assertEqual(len(object_list), expected_outcome)

    def test_form_in_create_edit_pages(self):
        """на страницы создания и редактирования заметки передаются формы"""
        for url in (self.url_add, self.url_edit):
            with self.subTest(url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
