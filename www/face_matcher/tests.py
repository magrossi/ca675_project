from django.test import TestCase
from face_matcher.models import Face, Actor, History, HistoryItem
from django.contrib.auth.models import User

class UserActorTestCase(TestCase):
    def setUp(self):
        User.objects.create_user('demo', 'demo@demo.com', 'demo')
        Actor.objects.create(name='famous actor', gender='M')

    def test_user_exists(self):
        user = User.objects.get(username='demo')
        actor = Actor.objects.get(name='famous actor')
        self.assertEqual(user.email, 'demo@demo.com')
        self.assertEqual(actor.gender, 'M')
