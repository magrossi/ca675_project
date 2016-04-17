from importlib import import_module
from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
from face_matcher.services.registration import RegistrationService


class RegistrationServiceTestCase(TestCase):
    def setUp(self):
        invalid_data = {
            'username': 'pewpewpew',
            'password1': 'lolcats'
        }
        valid_data = dict(invalid_data, **{'password2': invalid_data['password1']})
        mock_session = import_module(settings.SESSION_ENGINE).SessionStore()
        self.invalid_req = RequestFactory().post('/', invalid_data)
        self.valid_req = RequestFactory().post('/', valid_data)
        self.invalid_req.session, self.valid_req.session = mock_session, mock_session

    def test_register(self):
        self.assertFalse(RegistrationService(self.invalid_req).register())
        self.assertTrue(RegistrationService(self.valid_req).register())
