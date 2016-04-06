import os, os.path, sys, csv, django, helpers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from face_matcher.models import Face

# make this method asynchronous using celery
def build_dataset():
    data_img = list() # will store the processed image binary
    data_lbl = list() # will store the labeling information
    for face in Face.objects.all():
        data_img.append(helpers.get_nparray_from_img(face.full_face_path, face.bbox))
        data_lbl.append((face.id, 'A' if face.actor is not None else 'U'))

    # fit the model to the data and save the file for later use
    model = helpers.build_model(data_img)
    helpers.save_model(model)

    # create and save the dataset of eigenface file
    with open('dataset.dat', 'wb') as f:
        for index, eigenface in enumerate(model.transform(data_img)):
            face_id, face_source = data_lbl[index]
            f.write('"{}","{}","{}"\n'.format(face_id, face_source, ' '.join(map(str, eigenface))))

    print ''
    print 'Created model.dat and dataset.dat files'
    print 'PCA Explained Variance Ratio: {}'.format(sum(model.explained_variance_ratio_))
    print 'Obs.: if this number is not satisfactory try increasing the number of components'
    print ''

def main(argv):
    build_dataset()

if __name__ == "__main__":
   main(sys.argv[1:])
