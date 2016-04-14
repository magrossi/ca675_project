import os
import os.path
import csv
import django

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from lib.helpers import ImageLibrary
from django.contrib.auth.models import User
from face_matcher.models import Face, Actor

# Clean Actor and Face tables
Face.objects.all().delete()
Actor.objects.all().delete()

facescrub_dataset_file = 'facescrub_dataset.txt'

actor_ct = 0
faces_ct = 0
users_ct = 0

# Build Face and Actors based on the existance of the image file
with open(facescrub_dataset_file, 'rb') as dset:
    reader = csv.reader(dset, dialect='excel')
    next(reader, None)  # skip the headers

    # Create new Actors/Faces based on existing image files
    # First obtain a listing of all existing images (especially usefull when using S3)
    filenames = set(list(ImageLibrary.list_all()))

    actor = None # Actors are in order in the dataset so can leverage it
    for id, name, gender, url, bbox, sha256, relative_img_path in reader:
        # no need to check if individual file exists, just lookup in the set
        if (relative_img_path in filenames):
            # Create new Actor if needed
            if (actor is None or actor.name != name or actor.gender != gender.upper()):
                actor = Actor.objects.create(name=name, gender=gender.upper())
                actor.save()
                actor_ct += 1

            # Create the new face
            face = Face.objects.create(id = id,
                                       url = url,
                                       user = None,
                                       actor = actor,
                                       face_bbox = bbox,
                                       face_img_path = relative_img_path)
            face.save()
            faces_ct += 1

            if (settings.FACEREC_MAX_SEED_IMG > 0 and faces_ct >= settings.FACEREC_MAX_SEED_IMG):
                break

# Start the face id sequence from 120,000 reserving the previous ids for Actors
from django.db import connection
with connection.cursor() as c:
    c.execute('SELECT setval(\'face_matcher_face_id_seq\', 120000, FALSE);')

# Create a demo user with demo picture
if not User.objects.filter(username='demo').exists():
    user = User.objects.create_user('demo', 'demo@demo.com', 'demo')
    user.save()
    users_ct += 1
    face = Face.objects.create(url = '/media/dog.png',
                               user = user,
                               actor = None,
                               face_bbox = '0,0,100,100',
                               face_img_path = 'dog.png')
    user.face_set.add(face)
    user.save()
    faces_ct += 1

print ""
print "Seed Summary:"
print "   Users  {}".format(users_ct)
print "  Actors  {}".format(actor_ct)
print "   Faces  {}".format(faces_ct)
print ""
