from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from face_matcher.models import Actor, Face, History, HistoryItem


class ViewsTestCase(TestCase):
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
        negativeAssertFn(response, 'Log in')
        negativeAssertFn(response, 'Sign up')
        postiveAssertFn(response, 'Upload your image')
        postiveAssertFn(response, self.user.username)

    def _assert_on_login_page(self, response):
        self.assertContains(response, 'Log In')
        self.assertContains(response, 'LogIn')
        self.assertContains(response, 'Sign In')


class IndexViewTestCase(ViewsTestCase):
    def test_root_sessionless(self):
        self._assert_on_root_page(self.client.get('/'), False)

    def test_root_sessionfull(self):
        self._login_user()
        self._assert_on_root_page(self.client.get('/'))


class LoginViewTestCase(ViewsTestCase):
    def setUp(self):
        super(LoginViewTestCase, self).setUp()
        self.login_route = reverse('django.contrib.auth.views.login')
        self.incomplete_data = {'username': self.user.username}
        self.invalid_data = {'username': self.user.username, 'password': 'no'}
        self.valid_data = {'username': self.user.username, 'password': self.password}

    def test_login_index_sessionless(self):
        self._assert_on_login_page(self.client.get('/login/'))

    def test_empty_login(self):
        response = self.client.post(self.login_route, {})
        self._assert_on_login_page(response)

    def test_incomplete_login(self):
        response = self.client.post(self.login_route, self.incomplete_data)
        self._assert_on_login_page(response)

    def test_invalid_login(self):
        response = self.client.post(self.login_route, self.invalid_data)
        self._assert_on_login_page(response)

    def test_invalid_login(self):
        response = self.client.post(self.login_route, self.invalid_data)
        self._assert_on_login_page(response)

    def test_valid_login(self):
        response = self.client.post(self.login_route, self.valid_data, follow=True)
        self._assert_on_root_page(response)
