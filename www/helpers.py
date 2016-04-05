from PIL import Image, ImageOps
from sklearn.decomposition import RandomizedPCA
from sklearn.externals import joblib
from django.conf import settings
import os, os.path, tempfile, numpy as np

def get_size():
    return settings.FACEREC_IMG_SIZE

def get_n_components():
    return settings.FACEREC_COMPONENTS

def get_temp_filename():
    return os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()))

def open_image(filename):
    """
    """
    return Image.open(filename)

def pre_process_image(image, bbox):
    """
    bbox is x0,y0,x1,y1
    """
    # crop face if not already done so
    x0, y0, x1, y1 = bbox
    curr_width, curr_height = image.size
    if x1 <= curr_width and y1 <= curr_height:
        image = image.crop(bbox)

    # convert to greyscale
    image = ImageOps.grayscale(image)

    # resize to working size
    image = image.resize(get_size(), Image.ANTIALIAS)

    # equalize histogram
    image = ImageOps.equalize(image)

    return image

def get_nparray_from_img(filename, bbox):
    """
    """
    im = open_image(filename)
    im = pre_process_image(im, bbox)
    return np.asarray(im.getdata())

def build_model(dataset):
    pca = RandomizedPCA(n_components=get_n_components())
    pca.fit(dataset)
    return pca

def dump(obj, filename, compress_level):
    joblib.dump(obj, filename, compress=compress_level)

def load(filename):
    return joblib.load(filename)

def save_model(model):
    dump(model, 'model.dat', compress_level=3)

def load_model():
    return load('model.dat')
