from django.test import TestCase
from face_matcher.models import Face, Actor, History, HistoryItem
from django.contrib.auth.models import User
from lib.helpers import ImageLibrary

class StorageTests(TestCase):
    def setUp(self):
        self.sample_img_path = 'dog.png'
        self.sample_temp_file = 'please_delete_me.txt'

    def test_list_images(self):
        rel_filenames = list(ImageLibrary.list_all())
        self.assertTrue(len(rel_filenames) > 0)

    def test_process_image(self):
        buff = ImageLibrary.process_image(self.sample_img_path, (0,0,100,100))
        self.assertTrue(len(buff) > 0)

    def test_write_to_and_del_from_storage(self):
        # notice that this does not have to be an image
        ImageLibrary.save_image("test data", self.sample_temp_file)
        ImageLibrary.del_image(self.sample_temp_file)

class UserActorTestCase(TestCase):
    def setUp(self):
        User.objects.create_user('demo', 'demo@demo.com', 'demo')
        Actor.objects.create(name='famous actor', gender='M')

    def test_user_exists(self):
        user = User.objects.get(username='demo')
        actor = Actor.objects.get(name='famous actor')
        self.assertEqual(user.email, 'demo@demo.com')
        self.assertEqual(actor.gender, 'M')
