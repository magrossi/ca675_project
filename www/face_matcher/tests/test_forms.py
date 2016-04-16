import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

import face_matcher.tests
from face_matcher.forms import ImageUploadForm

IMG_FIXTURE_PATH = os.path.join(os.path.dirname(face_matcher.tests.__file__),
                                'fixtures/dog.png')


class FormsTestCase(TestCase):

    def _build_form(self, **kwargs):
        image = open(IMG_FIXTURE_PATH)
        upload = SimpleUploadedFile(image.name, image.read(), content_type='image/png')
        return ImageUploadForm(kwargs, dict({'image': upload}))

    def setUp(self):
        self.file_only_form = self._build_form()
        self.empty_form = ImageUploadForm()
        self.form = self._build_form(face_bbox=[1, 2, 3, 4],
                                     face_source_filter='all',
                                     max_results=8)

    def test_init(self):
        self.assertIsInstance(self.file_only_form, ImageUploadForm)
        self.assertIsInstance(self.empty_form, ImageUploadForm)

    def test_validate_with_blank_data(self):
        self.assertFalse(self.empty_form.is_valid())
        self.assertEqual(self.empty_form.errors, {})

    def test_validate_with_some_data(self):
        self.assertFalse(self.file_only_form.is_valid())
        self.assertEqual(self.file_only_form.errors, {
            'face_bbox': ['Please select/crop your face on photo.'],
            'face_source_filter': ['This field is required.'],
            'max_results': [u'This field is required.'],
        })
        self.assertEqual(self._build_form(face_bbox=[1, 2, 3, 4],
                                          max_results=8).errors, {
            'face_source_filter': ['This field is required.']
        })

    def test_validate_with_valid_data(self):
        self.assertTrue(self.form.is_valid())
        self.assertEqual(self.form.errors, {})
