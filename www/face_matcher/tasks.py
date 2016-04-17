import csv
from celery import shared_task
from django.db import connection
from django.conf import settings
from django.contrib.auth.models import User
from lib.findsimilars import FindSimilars
from lib.helpers import ImageLibrary, ModelBuilder
from models import History, Face, Actor


# ##################################################################### #
# WARNING:                                                              #
#   - All returned objects from these tasks must be JSON Serializable   #
#   - Usually is better to not return anything or return an id          #
# ##################################################################### #

@shared_task
def find_similars(history_id, similarity_method='cosine', face_source_filter='all',
                  max_results=10, job_options=['r', 'inline']):
    history = History.objects.get(id=history_id)
    try:
        FindSimilars.find(history, similarity_method=similarity_method,
                          face_source_filter=face_source_filter,
                          max_results=max_results, job_options=job_options)
    except Exception as e:
        history.status = History.ERROR
        history.output = str(e)
        history.save()
    return history.id


@shared_task
def build_datasets(method_threshold=1000, max_chunk_size=1000):
    data_img = list()  # will store img_path, bbox list for processing
    data_lbl = list()  # will store the labeling information

    for face in Face.objects.all():
        data_img.append((face.face_img_path, face.bbox))
        data_lbl.append((face.id, face.face_source))

    # Define which build dataset method to use based on how much data we have
    # Ex: 8Gb RAM is not enough to fit the whole dataset and not even enough
    #     to apply the model to the raw pre processed image data
    if len(data_img) <= method_threshold:
        # Not much data so can use performance efficient method
        # load and pre-process all images
        proc_data = list(ImageLibrary.process_images(data_img))
        # build model and apply transformations
        model, eigenfaces = ModelBuilder.build(proc_data)
    else:
        # Could be a lot of data, so use memory efficient method to avoid
        # out of memory exceptions
        model = ModelBuilder.build_from_iter(ImageLibrary.process_images(data_img), max_chunk_size)
        # second pass at the data just to apply the model
        # if we apply the model directly to the full data we will get an out of
        # memory exception as well for lower ram machines
        eigenfaces = list(ModelBuilder.apply_from_iter(model, ImageLibrary.process_images(data_img)))

    # save model
    ModelBuilder.dump(model)
    # save eigenface dataset
    ModelBuilder.dump_dataset(eigenfaces, data_lbl)


@shared_task
def seed(max_faces=1000):
    # Clean Actor and Face tables
    Face.objects.all().delete()
    Actor.objects.all().delete()
    # Facescrub Dataset used as an index
    facescrub_dataset_file = settings.FACESCRUB_DATASET_PATH
    # Counters
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

        actor = None  # Actors are in order in the dataset so can leverage it
        for id, name, gender, url, bbox, sha256, relative_img_path in reader:
            # no need to check if individual file exists, just lookup in the set
            if (relative_img_path in filenames):
                # Create new Actor if needed
                if (actor is None or actor.name != name or actor.gender != gender.upper()):
                    actor = Actor.objects.create(name=name, gender=gender.upper())
                    actor.save()
                    actor_ct += 1
                # Create the new face
                face = Face.objects.create(id=id, url=url, user=None, actor=actor,
                                           face_bbox=bbox, face_img_path=relative_img_path)
                face.save()
                faces_ct += 1

                if (max_faces > 0 and faces_ct >= max_faces):
                    break

    # Start the face id sequence from 120,000 reserving the previous ids for Actors
    with connection.cursor() as c:
        c.execute('SELECT setval(\'face_matcher_face_id_seq\', 120000, FALSE);')
    # Create a demo user with demo picture
    if not User.objects.filter(username='demo').exists():
        user = User.objects.create_user('demo', 'demo@demo.com', 'demo')
        user.save()
        users_ct += 1
        face = Face.objects.create(url='/media/dog.png', user=user, actor=None,
                                   face_bbox='0,0,100,100', face_img_path='dog.png')
        user.face_set.add(face)
        user.save()
        faces_ct += 1
    return (users_ct, actor_ct, faces_ct)
