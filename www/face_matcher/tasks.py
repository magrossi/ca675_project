from celery import shared_task
from lib.findsimilars import FindSimilars
from lib.helpers import ImageLibrary, ModelBuilder
from models import History, Face

# ##################################################################### #
# WARNING:                                                              #
#   - All returned objects from these tasks must be JSON Serializable   #
#   - Usually is better to not return anything or return an id          #
# ##################################################################### #

@shared_task
def find_similars(history_id, similarity_method='cosine', face_source_filter='all', max_results=10, job_options=['r', 'inline']):
    history = History.objects.get(id=history_id)
    FindSimilars.find(history, similarity_method=similarity_method, face_source_filter=face_source_filter, max_results=max_results, job_options=job_options)
    return history.id

@shared_task
def build_datasets(method_threshold=1000, max_chunk_size=1000):
    data_img = list() # will store img_path, bbox list for processing
    data_lbl = list() # will store the labeling information

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
