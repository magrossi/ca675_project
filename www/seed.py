import os, os.path, csv, django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from face_matcher.models import Face, Actor

facescrub_dataset_file = 'facescrub_dataset.txt'

# Read facescrub_dataset.txt
# Format: 'id', 'name', 'gender', 'url', 'bbox', 'sha256', 'relative_img_path'

# To build Face and Actors based on the existance of the image file
with open(facescrub_dataset_file, 'rb') as dset:
    reader = csv.reader(dset, dialect='excel')
    next(reader, None)  # skip the headers

    # Create new Actors/Faces based on existing image files
    actor = None # Actors are in order in the dataset so can leverage it
    for id, name, gender, url, bbox, sha256, relative_img_path in reader:
        filename = os.path.join(settings.IMG_BASE_DIR, relative_img_path)
        if (os.path.exists(filename)):
            # Create new Actor if needed
            if (actor is None or actor.name != name or actor.gender != gender.upper()):
                actor = Actor.objects.create(name=name, gender=gender.upper())
                actor.save()

            # Create the new face
            face = Face.objects.create(url = url,
                                       user = None,
                                       actor = actor,
                                       face_bbox = bbox,
                                       face_img_path = relative_img_path)
            face.save()

# Create a demo user with demo picture
from django.contrib.auth.models import User

user = User.objects.create_user('demo', 'demo@demo.com', 'demo')
user.save()

face = Face.objects.create(url = '/media/dog.png',
                           user = user,
                           actor = None,
                           face_bbox = '0,0,100,100',
                           face_img_path = 'dog.png')

user.face_set.add(face)
user.save()
