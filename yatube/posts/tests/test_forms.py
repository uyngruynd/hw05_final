import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='МухамедАли')
        cls.group = Group.objects.create(
            title='Спорт',
            slug='test3',
            description='Спортивные блоги'
        )
        Post.objects.create(
            text='Переживать из-за ошибок – самая грубая ошибка, '
                 'которую только можно придумать',
            author=cls.author,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create(username='МайкТайсон')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

        self.guest_client = Client()

    def test_create_post(self):
        """
        При отправке валидной формы создается новая запись в БД и происходит
        редирект.
        """
        posts_cnt = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Страх – это самое большое препятствие для обучения.',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': 'МайкТайсон'}))
        self.assertEqual(Post.objects.count(), posts_cnt + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Страх – это самое большое препятствие для обучения.',
                group=self.group.id,
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        """При отправке валидной формы происходит изменение поста в БД."""
        post_before = Post.objects.last()
        text_before = post_before.text
        text_after = 'Я памятник себе воздвиг нерукотворный...'
        self.authorized_author.post(
            reverse('posts:post_edit', kwargs={'post_id': post_before.pk}),
            data={'text': text_after},
            follow=True
        )
        post_after = Post.objects.get(pk=post_before.pk)
        self.assertNotEqual(post_after.text, text_before)

    def test_create_comment_authorized(self):
        """
        Проверка возможности создания комментария авторизованным пользователем
        и редирект на страницу поста.
        """
        post = Post.objects.last()
        comments_before = post.comments.all().count()
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.pk}),
            data={'text': 'без комментариев...'},
            follow=True
        )
        comments_after = post.comments.all().count()
        self.assertNotEqual(comments_before, comments_after)
        self.assertTrue(
            Comment.objects.filter(
                post=post.id,
                text='без комментариев...',
            ).exists()
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': post.id}))

    def test_create_comment_guest(self):
        """
        Проверка невозможности создания комментария неавторизованным
        пользователем.
        """
        post = Post.objects.last()
        comments_before = post.comments.all().count()
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.pk}),
            data={'text': 'без комментариев...'},
            follow=True
        )
        comments_after = post.comments.all().count()
        self.assertEqual(comments_before, comments_after)
