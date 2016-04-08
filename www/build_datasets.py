import os, os.path, sys, csv, django, time
from lib.helpers import ImageLibrary, ModelBuilder

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from face_matcher.models import Face

# make this method asynchronous using celery
def build_dataset():
    start_time = time.time()

    data_img = list() # will store img_path, bbox list for processing
    data_lbl = list() # will store the labeling information

    for face in Face.objects.all():
        data_img.append((face.face_img_path, face.bbox))
        data_lbl.append((face.id, face.face_source))

    # load and pre-process all images
    proc_data = list(ImageLibrary.process_images(data_img))
    # build model and apply transformations
    model, eigenfaces = ModelBuilder.build(proc_data)
    # save model
    ModelBuilder.dump(model)
    # save eigenface dataset
    ModelBuilder.dump_dataset(eigenfaces, data_lbl)

    elapsed_time = time.time() - start_time

    print ''
    print 'Created model and eigenface data files in {} seconds'.format(elapsed_time)
    print 'PCA Explained Variance Ratio: {}%'.format(100.0*sum(model.explained_variance_ratio_))
    print 'Obs.: if this number is not satisfactory try increasing the number of components'
    print ''

def main(argv):
    build_dataset()

if __name__ == "__main__":
   main(sys.argv[1:])
