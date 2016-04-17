from django.test import TestCase
from face_matcher.models import History
from face_matcher.presenters.history import HistoryJson, HistoryIndex


class PresentersTestCase(TestCase):
    fixtures = ['users.json', 'actors.json', 'faces.json', 'histories.json',
                'history_items.json']


class HistoryJsonTestCase(PresentersTestCase):
    def setUp(self):
        self.unfinished_history = History.objects.filter(status='P').first()
        self.finished_history = History.objects.filter(status='F').first()
        self.unfinished_presentation = HistoryJson(self.unfinished_history).present()
        self.finished_presentation = HistoryJson(self.finished_history).present()

    def test_present_unfinished_data(self):
        self.assertFalse(self.unfinished_history.finished)
        self.assertEqual(self.unfinished_presentation, {
            'status': 'P',
            'status_label_class': 'warning',
        })

    def test_present_finished_data(self):
        self.assertTrue(self.finished_history.finished)
        self.assertEqual(self.finished_presentation, {
            'status': 'F',
            'status_label_class': 'success',
            'generated': '11.68 sec',
            'history_items': [{'image': 'http://img.dailymail.co.uk/img/pix2/adamsandlerR140502_329x450.jpg',
                               'similarity_score': '110.00'}],
            'status_string': 'Finished',
            'top_matcher_name': 'Adam Sandler',
            'top_matcher_similarity_score': '110.00',
            'top_matcher_source': 'A'
        })


class HistoryIndexTestCase(PresentersTestCase):
    def setUp(self):
        self.histories = History.objects.all()
        self.page_1_presentation = HistoryIndex(self.histories, 1).present()
        self.page_n_presentation = HistoryIndex(self.histories, 100 * 100).present()

    def test_present_paged_data(self):
        self.assertTrue('history' in self.page_1_presentation)
        self.assertEqual(len(self.page_1_presentation['history']), 2)
        self.assertEqual(len(self.page_n_presentation['history']),
                         len(self.page_1_presentation['history']))
        self.assertEqual(self.page_n_presentation['history'][0].id, self.histories[0].id)
        self.assertEqual(self.page_1_presentation['history'][0].id, self.histories[0].id)
