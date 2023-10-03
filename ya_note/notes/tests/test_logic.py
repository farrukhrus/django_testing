from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestCreate(TestCase):
    SUCCESS_REDIRECT = reverse('notes:success')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.anon_client = Client()

        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'slug': 'note',
        }

        cls.add_url = reverse('notes:add')

    def test_anonymous_user_cant_create_note(self):
        """
        Анонимный пользователь не может создать заметку.
        """
        init_cnt = Note.objects.count()
        response = self.anon_client.post(self.add_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), init_cnt)

    def test_user_can_create_note(self):
        """
        Залогиненный пользователь может создать заметку.
        """
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_REDIRECT)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        new_note = Note.objects.get()

        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_empty_slug(self):
        """
        Если при создании заметки не заполнен slug, то он формируется
        автоматически, с помощью функции pytils.translit.slugify
        """
        self.form_data.pop('slug')
        self.author_client.post(self.add_url, data=self.form_data)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestEditDelete(TestCase):
    NOTE_TEXT = 'Текст'
    NEW_NOTE_TEXT = 'Новый текст'
    SUCCESS_REDIRECT = reverse('notes:success')

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.note = Note.objects.create(
            title='Заголовок',
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug='test',
        )
        cls.form_data = {
            'title': cls.note.title,
            'text': cls.NEW_NOTE_TEXT,
            'slug': cls.note.slug,
        }

        cls.reader = User.objects.create(username='Гость')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_author_can_edit_note(self):
        """
        Пользователь может редактировать свои заметки
        """
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.SUCCESS_REDIRECT)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_author_can_delete_note(self):
        """
        Пользователь может удалять свои заметки
        """
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.SUCCESS_REDIRECT)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_guest_cant_edit_others_note(self):
        """
        Пользователь не может редактировать чужие заметки
        """
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_guest_cant_delete_others_note(self):
        """
        Пользователь не может удалять чужие заметки
        """
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
