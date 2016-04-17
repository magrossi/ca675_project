from importlib import import_module
from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.core.files.uploadedfile import SimpleUploadedFile
from face_matcher.services.registration import RegistrationService
from face_matcher.services.matcher import FaceMatcherService
from face_matcher.tests import IMG_FIXTURE_PATH


class BaseServiceTestCase(TestCase):
    fixtures = ['users.json']

    def _patch_req_session(self, req):
        req.session = import_module(settings.SESSION_ENGINE).SessionStore()
        req.user = User.objects.first()

    def setUp(self):
        self.invalid_req = RequestFactory().post('/', {})
        self._patch_req_session(self.invalid_req)


class RegistrationServiceTestCase(BaseServiceTestCase):
    def setUp(self):
        super(RegistrationServiceTestCase, self).setUp()
        self.valid_req = RequestFactory().post('/', {
            'username': 'pewpewpew',
            'password1': 'lolcats',
            'password2': 'lolcats',
        })
        self._patch_req_session(self.valid_req)

    def test_register(self):
        self.assertFalse(RegistrationService(self.invalid_req).register())
        self.assertTrue(RegistrationService(self.valid_req).register())


class FaceMatcherServiceTestCase(BaseServiceTestCase):
    def setUp(self):
        super(FaceMatcherServiceTestCase, self).setUp()
        image = open(IMG_FIXTURE_PATH)
        upload = SimpleUploadedFile(image.name, image.read(), content_type='image/png')
        self.valid_req = RequestFactory().post('/', {
            'image': upload,
            'face_bbox': [1, 2, 3, 4],
            'face_source_filter': 'all',
            'max_results': 8,
        })
        self._patch_req_session(self.valid_req)

    def test_match_upload(self):
        self.assertFalse(FaceMatcherService(self.invalid_req).match_upload())
        self.assertTrue(FaceMatcherService(self.valid_req).match_upload())
