from collections import namedtuple
from django.test import TestCase
from django.contrib.auth.models import User
from django.template import Context, Template

HEADER_TEMPLATE_STR = '{% load face_matcher_extras %}{% header %}'
MULTIPLY_POSITIVE_TEMPLATE_STR = '{% load face_matcher_extras %}{% multiply_100 0.15 %}'
MULTIPLY_NEGATIVE_TEMPLATE_STR = '{% load face_matcher_extras %}{% multiply_100 -0.15 %}'


class TemplateTagsCase(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        mock_request = namedtuple('Request', ['path'])
        self.user = User.objects.first()
        self.headerTemplate = Template(HEADER_TEMPLATE_STR)
        self.posMultiTemplate = Template(MULTIPLY_POSITIVE_TEMPLATE_STR)
        self.negMultiTemplate = Template(MULTIPLY_NEGATIVE_TEMPLATE_STR)
        self.context_at_root = Context({'user': self.user,
                                        'request': mock_request(path='/')})
        self.context_at_faces = Context({'user': self.user,
                                         'request': mock_request(path='/faces')})

    def test_header_at_root_route(self):
        html = self.headerTemplate.render(self.context_at_root)
        self.assertTrue('href=" #about"' in html)
        self.assertTrue(self.user.username in html)

    def test_header_at_faces_route(self):
        html = self.headerTemplate.render(self.context_at_faces)
        self.assertTrue('href="/#about"' in html)
        self.assertTrue(self.user.username in html)

    def test_postive_multiply_100(self):
        self.assertEqual(self.posMultiTemplate.render(Context({})), "15.00")

    def test_negative_multiply_100(self):
        self.assertEqual(self.negMultiTemplate.render(Context({})), "-15.00")
