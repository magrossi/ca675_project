from django.test import TestCase
from face_matcher.models import Upload
from django.contrib.auth.models import User


class UploadTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='john',
                                             email='jlennon@beatles.com',
                                             password='glass onion')
        self.img_url = 'https://www.google.ie/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png'

    def test_can_create_users(self):
        Upload.objects.create(url=self.img_url, user=self.user)
        Upload.objects.create(url=self.img_url, user=self.user)
        for upload in Upload.objects.all():
            self.assertEqual(upload.url, self.img_url)
            self.assertEqual(upload.user.email, self.user.email)
