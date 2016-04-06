from django.test import TestCase
from face_matcher.models import Face, Actor, History, HistoryItem
from django.contrib.auth.models import User
from findsimilars import FindSimilars

class HistoryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.get(username='demo')
        cls.face = cls.user.face_set.first()

    def find_similars_default(self):
        history = History.objects.create(user=self.user, in_face=self.face)
        history.save()
        self.assertEqual(history.user, self.user)
        FindSimilars.find(history)
        self.assertEqual(history.historyitem_set.all(), 10)
