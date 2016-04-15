from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.urlresolvers import resolve


class UrlsTestCase(TestCase):
    urls = 'face_matcher.urls'

    def _get_url_and_resolver(self, name):
        url = reverse(name)
        return url, resolve(url)

    def test_root(self):
        url, resolver = self._get_url_and_resolver('index')
        self.assertEqual(url, '/')
        self.assertEqual(resolver.view_name, 'index')

    def test_faces(self):
        url, resolver = self._get_url_and_resolver('faces')
        self.assertEqual(url, '/faces/')
        self.assertEqual(resolver.view_name, 'faces')

    def test_faces(self):
        url, resolver = self._get_url_and_resolver('registration')
        self.assertEqual(url, '/registration/')
        self.assertEqual(resolver.view_name, 'registration')
