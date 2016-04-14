from django.test import TestCase
from face_matcher.models import Actor, Face, History, HistoryItem
from django.contrib.auth.models import User


class BaseModelTestCase(TestCase):
    fixtures = ['users.json', 'actors.json', 'faces.json', 'histories.json',
                'history_items.json']


class ActorTestCase(BaseModelTestCase):
    def test_string_representation(self):
        first_actor = Actor.objects.first()
        last_actor = Actor.objects.last()
        self.assertEqual(str(first_actor), first_actor.name)
        self.assertEqual(str(last_actor), last_actor.name)


class FaceTestCase(BaseModelTestCase):
    def test_string_representation(self):
        first_face = Face.objects.first()
        last_face = Face.objects.last()
        self.assertEqual(str(first_face), first_face.url)
        self.assertEqual(str(last_face), last_face.url)


class HistoryTestCase(BaseModelTestCase):
    def test_string_representation(self):
        first_history = History.objects.first()
        last_history = History.objects.last()
        self.assertEqual(str(first_history), "{}: {}".format(first_history.created_at,
                                                             first_history.status))
        self.assertEqual(str(last_history), "{}: {}".format(last_history.created_at,
                                                            last_history.status))


class HistoryItemTestCase(BaseModelTestCase):
    def test_string_representation(self):
        first_item = HistoryItem.objects.first()
        last_item = HistoryItem.objects.last()
        self.assertEqual(str(first_item), str(first_item.similarity_score))
        self.assertEqual(str(last_item), str(last_item.similarity_score))
