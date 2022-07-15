from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Post, Group

User = get_user_model()

urls_pub = {
    '/': 'posts/index.html',
    '/group/test/': 'posts/group_list.html',
    '/profile/Анна Ахматова/': 'posts/profile.html',
    '/posts/1/': 'posts/post_detail.html',
}

urls_user = {'/create/': 'posts/create_post.html'}
urls_author = {'/posts/1/edit/': 'posts/create_post.html'}
url_unknown = '/unknown_page/'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='Анна Ахматова')
        cls.group = Group.objects.create(
            title='Поэзия',
            slug='test',
            description='Наши поэты'
        )
        cls.post = Post.objects.create(
            text='Один идет прямым путем, другой идет по кругу',
            author=cls.author,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()

        self.user = User.objects.create(username='Саша Пушкин')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.authorized_author = Client()
        self.authorized_author.force_login(self.author)

    def test_url_exists_guest(self):
        """Страницы доступны любому посетителю."""
        for url in urls_pub.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_user(self):
        """Страницы доступны авторизованному пользователю."""
        urls = {**urls_pub, **urls_user}
        for url in urls.keys():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_exists_author(self):
        """Страницы доступны автору."""
        urls = {**urls_pub, **urls_author}
        for url in urls.keys():
            with self.subTest(url=url):
                response = self.authorized_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_template(self):
        """URL-адрес использует соответствующие шаблоны."""
        urls = {**urls_pub, **urls_author}
        for url, template in urls.items():
            with self.subTest(url=url):
                response = self.authorized_author.get(url)
                self.assertTemplateUsed(response, template)

    def test_redirect_anonymous_on_admin_login(self):
        """
        URL-адрес перенаправит анонимного пользователя на страницу логина.
        """
        for url in urls_user.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_url_not_found(self):
        """Страница не найдена."""
        response = self.authorized_client.get(url_unknown)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
