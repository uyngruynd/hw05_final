import shutil
import tempfile

import django.db.models.fields.files
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from django.core.paginator import Page
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, Follow

User = get_user_model()
POSTS_ON_PAGE = 10
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Петя')
        cls.group = Group.objects.create(
            title='Поэзия',
            slug='test',
            description='Поэзия'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        Post.objects.bulk_create(
            Post(
                text=f'Стихотворение№{i}',
                author=cls.author,
                group=cls.group,
                image=cls.uploaded,
            ) for i in range(POSTS_ON_PAGE)
        )
        other_group = Group.objects.create(
            title='Кино',
            slug='test2',
            description='Группа о кино'
        )
        cls.other_post = Post.objects.create(
            text='Твин Пикс',
            author=cls.author,
            group=other_group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

        self.user = self.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.follower = User.objects.create(username='Дядя Вася')
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)

        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_templates = {
            reverse('posts:main'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Петя'}):
                'posts/profile.html',

            reverse('posts:post_detail', kwargs={'post_id': 1}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': 1}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in pages_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_contains_ten_records(self):
        """Количество постов на страницах с паджинатором равно 10."""
        paginator_names = [reverse('posts:main'),
                           reverse('posts:group_list',
                                   kwargs={'slug': 'test'}),
                           reverse('posts:profile',
                                   kwargs={'username': 'Петя'}),
                           ]
        for reverse_name in paginator_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 POSTS_ON_PAGE)

    def test_main_page_show_correct_context(self):
        """Шаблон main сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:main'))
        form_field = response.context.get('page_obj')
        self.assertIsInstance(form_field, Page)

    def test_group_list_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test'})
        )
        pages = response.context.get('page_obj')
        for page in pages:
            with self.subTest(page=page):
                self.assertEqual(page.group, self.group)

        form_fields = {
            'group': Group,
            'page_obj': Page,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Петя'})
        )
        pages = response.context.get('page_obj')
        for page in pages:
            with self.subTest(page=page):
                self.assertEqual(page.author, self.author)

        form_fields = {
            'author': User,
            'page_obj': Page,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        form_field = response.context.get('post')
        self.assertIsInstance(form_field, Post)
        self.assertEqual(form_field.id, 1)

    def test_create_post_edit_page_show_correct_context(self):
        """
        Шаблон create_post(создание) сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_create_page_show_correct_context(self):
        """
        Шаблон create_post(изменение) сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_find_post_with_group_in_pages(self):
        """Проверка наличия поста, связанного с группой на страницах"""
        pages_with_group_post = [reverse('posts:main'),
                                 reverse('posts:group_list',
                                         kwargs={'slug': 'test2'}),
                                 reverse('posts:profile',
                                         kwargs={'username': 'Петя'}),
                                 ]
        for page in pages_with_group_post:
            response = self.authorized_client.get(page)
            with self.subTest(page=page):
                posts = response.context.get('page_obj').object_list
                self.assertIn(self.other_post, posts)

    def test_find_no_post_with_group_in_pages(self):
        """
        Проверка отсутствия поста, связанного с группой на странице другой
        группы.
        """
        page = reverse('posts:group_list', kwargs={'slug': 'test'})
        response = self.authorized_client.get(page)
        posts = response.context.get('page_obj').object_list
        self.assertNotIn(self.other_post, posts)

    def test_images_on_the_pages(self):
        """Проверка наличия картинки в постах на страницах"""
        value = 'image'
        expected = django.db.models.fields.files.ImageFieldFile
        pages_with_pics = {
            'posts:main': {},
            'posts:profile': {'username': 'Петя'},
            'posts:group_list': {'slug': 'test'},
        }
        for page, params in pages_with_pics.items():
            response = self.authorized_client.get(reverse(page, kwargs=params))
            page_obj = response.context.get('page_obj')
            for post in page_obj:
                with self.subTest(post=post):
                    form_field = getattr(post, value)
                    self.assertIsInstance(form_field, expected)

        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1}))
        form_field = getattr(response.context.get('post'), value)
        self.assertIsInstance(form_field, expected)

    def test_index_page_is_cached(self):
        """Проверка создания кэша для списка постов главной страницы"""
        response = self.authorized_client.get(reverse('posts:main'))
        content_before = response.content

        Post.objects.all().delete()

        response = self.authorized_client.get(reverse('posts:main'))
        content_after_del = response.content
        self.assertEqual(content_before, content_after_del)

        cache.clear()

        response = self.authorized_client.get(reverse('posts:main'))
        content_after_clear = response.content
        self.assertNotEqual(content_before, content_after_clear)

    def test_following_process_is_available(self):
        """
        Проверка возможности подписки/отписки для авторизованного пользователя.
        """
        cnt_before = Follow.objects.filter(user_id=self.follower.id,
                                           author_id=self.author.id).count()
        self.follower_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username})
        )
        cnt_after_follow = Follow.objects.filter(
            user_id=self.follower.id,
            author_id=self.author.id
        ).count()
        self.assertNotEqual(cnt_before, cnt_after_follow)

        self.follower_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author.username})
        )
        cnt_after_del = Follow.objects.filter(user_id=self.follower.id,
                                              author_id=self.author.id).count()
        self.assertEqual(cnt_before, cnt_after_del)

    def test_following_posts_is_available(self):
        """
        Проверка наличия постов по подписке на странице подписчика,
        проверка отсутствия постов у пользователя, не подписанного ни на кого.
        """
        self.follower_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username})
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        cnt_follower = response.context.get('page_obj').paginator.count
        self.assertNotEqual(cnt_follower, 0)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        cnt_user = response.context.get('page_obj').paginator.count
        self.assertEqual(cnt_user, 0)
