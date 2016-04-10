import os, os.path, sys, csv, django, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from lib.helpers import ImageLibrary, ModelBuilder
from face_matcher.tasks import build_datasets

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def build_dataset():
    start_time = time.time()

    # execute async but waits for it to finish
    async_res = build_datasets.delay()
    async_state = async_res.state

    print 'Starting async execution in state: {}'.format(async_state)

    while not async_res.ready():
        time.sleep(5)
        if async_state != async_res.state:
            async_state = async_res.state
            print 'Execution state changed to: {}'.format(async_state)

    elapsed_time = time.time() - start_time

    print 'Finished execution in state: {}'.format(async_state)
    print ''
    if async_res.failed():
        ex = async_res.result
        print 'Failed to execute task.'
        print 'Message: {}'.format(ex)
    else:
        model = ModelBuilder.load()
        faces = file_len(ModelBuilder.dataset_filename)
        print 'Created model and eigenface data files in {} seconds'.format(elapsed_time)
        print 'Number of faces included in the model: {}'.format(faces)
        print 'PCA Explained Variance Ratio: {}%'.format(100.0*sum(model.explained_variance_ratio_))
        print 'Obs.: if this number is not satisfactory try increasing the number of components'
    print ''

def main(argv):
    build_dataset()

if __name__ == "__main__":
   main(sys.argv[1:])
