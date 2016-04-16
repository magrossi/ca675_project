from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from face_matcher.models import Actor, Face, History, HistoryItem


class ViewTestCase(TestCase):
    fixtures = ['users.json', 'actors.json', 'faces.json', 'histories.json',
                'history_items.json']

    def setUp(self):
        self.user = User.objects.first()
        self.password = 'lol'
        self.user.set_password('lol')
        self.user.save()

    def _login_user(self):
        self.assertTrue(self.client.login(username=self.user.username,
                                          password=self.password))

    def _assert_on_root_page(self, response, is_authenticated=True):
        postiveAssertFn = self.assertContains if is_authenticated else self.assertNotContains
        negativeAssertFn = self.assertNotContains if is_authenticated else self.assertContains
        negativeAssertFn(response, 'Log In')
        negativeAssertFn(response, 'Sign Up')
        postiveAssertFn(response, 'Upload your image')
        postiveAssertFn(response, 'fa-sign-out')

    def _assert_on_login_page(self, response):
        self.assertContains(response, 'Log In')
        self.assertContains(response, 'Sign Up')
        self.assertContains(response, 'Sign In')

    def _assert_on_registration_page(self, response):
        self.assertContains(response, 'Log In')
        self.assertContains(response, 'Registration')
        self.assertContains(response, 'Register')

    def _assert_on_matcher_page(self, response):
        self.assertContains(response, 'Upload your photo')
        self.assertContains(response, 'fa-sign-out')
        self.assertContains(response, 'History')


class IndexViewTestCase(ViewTestCase):
    def test_root_sessionless(self):
        self._assert_on_root_page(self.client.get('/'), False)

    def test_root_sessionfull(self):
        self._login_user()
        self._assert_on_root_page(self.client.get('/'))


class LoginViewTestCase(ViewTestCase):
    def setUp(self):
        super(LoginViewTestCase, self).setUp()
        self.login_route = reverse('django.contrib.auth.views.login')
        self.incomplete_data = {'username': self.user.username}
        self.invalid_data = {'username': self.user.username, 'password': 'no'}
        self.valid_data = {
            'username': self.user.username,
            'password': self.password
        }

    def test_login_index_sessionless(self):
        self._assert_on_login_page(self.client.get(self.login_route))

    def test_empty_login(self):
        response = self.client.post(self.login_route, {})
        self._assert_on_login_page(response)

    def test_incomplete_login(self):
        response = self.client.post(self.login_route, self.incomplete_data)
        self._assert_on_login_page(response)

    def test_invalid_login(self):
        response = self.client.post(self.login_route, self.invalid_data)
        self._assert_on_login_page(response)

    def test_valid_login(self):
        response = self.client.post(self.login_route, self.valid_data, follow=True)
        self._assert_on_matcher_page(response)


class RegistrationViewTestCase(ViewTestCase):
    def setUp(self):
        super(RegistrationViewTestCase, self).setUp()
        self.reg_route = '/registration/'
        self.new_username = 'Lolcats'
        self.incomplete_data = {'username': self.new_username}
        self.invalid_data = dict(self.incomplete_data, **{
            'password1': self.password,
            'password2': 'no'
        })
        self.valid_data = dict(self.invalid_data, **{'password2': self.password})
        self.duplicate_data = dict(self.valid_data, **{'username': self.user.username})

    def test_registration_index_sessionless(self):
        self._assert_on_registration_page(self.client.get(self.reg_route))

    def test_empty_registration(self):
        response = self.client.post(self.reg_route, {})
        self._assert_on_registration_page(response)
        self.assertContains(response, 'This field is required')

    def test_empty_registration(self):
        response = self.client.post(self.reg_route, self.incomplete_data)
        self._assert_on_registration_page(response)
        self.assertContains(response, 'This field is required')

    def test_invalid_data_registration(self):
        response = self.client.post(self.reg_route, self.invalid_data)
        self._assert_on_registration_page(response)
        self.assertContains(response, 'The two password fields didn&#39;t match')

    def test_duplicate_data_registration(self):
        response = self.client.post(self.reg_route, self.duplicate_data)
        self._assert_on_registration_page(response)
        self.assertContains(response, 'A user with that username already exists')

    def test_valid_registration(self):
        response = self.client.post(self.reg_route, self.valid_data, follow=True)
        self._assert_on_matcher_page(response)


class MatcherViewTestCase(ViewTestCase):
    def setUp(self):
        super(MatcherViewTestCase, self).setUp()
        self.matcher_route = '/matcher/'
        self._login_user()

    def test_matcher_index(self):
        self._assert_on_matcher_page(self.client.get(self.matcher_route))

    def test_empty_upload(self):
        response = self.client.post(self.matcher_route, {})
        self._assert_on_matcher_page(response)
        self.assertContains(response, 'This field is required')
