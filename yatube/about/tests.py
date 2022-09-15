from http import HTTPStatus

from django.test import Client, TestCase

urls = {
    '/about/author/': 'about/author.html',
    '/about/tech/': 'about/tech.html'
}


class StaticPagesURLTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exists(self):
        for url in urls.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_correct_template(self):
        for url, template in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
