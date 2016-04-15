from django.test import TestCase
from face_matcher.models import Actor, Face, History, HistoryItem
from django.contrib.auth.models import User


class BaseModelTestCase(TestCase):
    Model = None
    fixtures = ['users.json', 'actors.json', 'faces.json', 'histories.json',
                'history_items.json']

    def setUp(self):
        if self.Model:
            self.entities = self.Model.objects.all()
            self.first_entity = self.entities[0]
            self.last_entity = self.Model.objects.last()


class ActorTestCase(BaseModelTestCase):
    def setUp(self):
        self.Model = Actor
        super(ActorTestCase, self).setUp()

    def test_string_representation(self):
        self.assertEqual(str(self.first_entity), self.first_entity.name)
        self.assertEqual(str(self.last_entity), self.last_entity.name)

    def test_ordering_by_name(self):
        self.assertTrue(self.first_entity.name < self.last_entity.name)


class FaceTestCase(BaseModelTestCase):
    def setUp(self):
        self.Model = Face
        super(FaceTestCase, self).setUp()

    def test_string_representation(self):
        self.assertEqual(str(self.first_entity), self.first_entity.url)
        self.assertEqual(str(self.last_entity), self.last_entity.url)

    def test_ordering_by_created_at(self):
        self.assertTrue(self.first_entity.created_at < self.last_entity.created_at)

    def test_face_source(self):
        self.assertEqual(self.first_entity.face_source, 'A')
        self.assertEqual(self.last_entity.face_source, 'A')

    def test_bbox(self):
        self.assertEqual(self.first_entity.bbox, [62, 90, 231, 259])
        self.assertEqual(self.last_entity.bbox, [22, 98, 207, 283])

class HistoryTestCase(BaseModelTestCase):
    def setUp(self):
        self.Model = History
        super(HistoryTestCase, self).setUp()

    def test_string_representation(self):
        self.assertEqual(str(self.first_entity), "{}: {}".format(self.first_entity.created_at,
                                                                 self.first_entity.status))
        self.assertEqual(str(self.last_entity), "{}: {}".format(self.last_entity.created_at,
                                                                self.last_entity.status))

    def test_ordering_by_inverse_created_at(self):
        self.assertTrue(self.first_entity.created_at > self.last_entity.created_at)


class HistoryItemTestCase(BaseModelTestCase):
    def setUp(self):
        self.Model = HistoryItem
        super(HistoryItemTestCase, self).setUp()

    def test_string_representation(self):
        self.assertEqual(str(self.first_entity), str(self.first_entity.similarity_score))
        self.assertEqual(str(self.last_entity), str(self.last_entity.similarity_score))

    def test_ordering_by_inverse_similarity_score(self):
        self.assertTrue(self.first_entity.similarity_score > self.last_entity.similarity_score)
