from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()

NAME_LEN: int = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='МахатмаГанди')
        cls.group = Group.objects.create(
            title='Политика',
            slug='test',
            description='Блоги великих политиков'
        )
        cls.post = Post.objects.create(
            text='Свобода ничего не стоит, если она не включает в себя '
                 'свободу ошибаться.',
            author=cls.author,
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """В поле __str__  объекта post записано значение post.text[:15]."""
        post = PostModelTest.post
        expected_object_name = post.text[:NAME_LEN]
        self.assertEqual(expected_object_name, str(post))

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
