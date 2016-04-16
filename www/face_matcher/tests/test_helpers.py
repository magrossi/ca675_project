import os
import os.path
import time

import redis
from testfixtures import TempDirectory
from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from lib.helpers import ImageLibrary
from face_matcher.models import Actor, Face, History
from face_matcher.tasks import find_similars, seed, build_datasets


class ImageLibraryTestCase(TestCase):
    def setUp(self):
        self.sample_img_path = 'dog.png'
        self.sample_temp_file = 'please_delete_me.txt'

    def test_list_images(self):
        rel_filenames = list(ImageLibrary.list_all())
        self.assertTrue(len(rel_filenames) > 0)

    def test_process_image(self):
        buff = ImageLibrary.process_image(self.sample_img_path, (0, 0, 100, 100))
        self.assertTrue(len(buff) > 0)

    def test_write_to_and_del_from_storage(self):
        ImageLibrary.save_image("test data", self.sample_temp_file)
        ImageLibrary.del_image(self.sample_temp_file)


class ModelBuilderTestCase(TestCase):
    def setUp(self):
        # Seed the database from the facescrub index and available images
        seed(max_faces=50)
        # save current working dir
        self.def_dir = os.getcwd()
        # change curret directory to a temp dir
        self.dir = TempDirectory()
        os.chdir(self.dir.path)
        # by changing the current directory we change
        # the location where the .dat files will be created

    def tearDown(self):
        # change current directory back to original
        os.chdir(self.def_dir)
        # delete temp directory
        self.dir.cleanup()

    def test_seed(self):
        self.assertTrue(Face.objects.all().count() > 0)
        self.assertTrue(Actor.objects.all().count() > 0)
        self.assertTrue(User.objects.all().count() > 0)

    def find_similars(self):
        # build or rebuild the datasets
        build_datasets(method_threshold=1000000)
        # find the demo user and get its first face
        user = User.objects.filter(username='demo')
        face = user.face_set.first()
        # create a new history item
        history = History.objects.create(user=user, in_face=face)
        history.save()
        # call find similars
        r = find_similars.delay(history.id)
        # wait for it to finish
        while not async_res.ready():
            time.sleep(1)
        # state must be success
        self.assertTrue(not r.failed())
        history_after = History.objects.get(pk=int(r.result))
        # both history items must be the same
        self.assertTrue(history_after.id == history.id)
        # must have found at least one similar face
        self.assertTrue(len(list(history_afterhistoryitem_set.all())) > 0)
