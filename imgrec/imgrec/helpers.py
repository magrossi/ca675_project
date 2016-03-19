from PIL import Image, ImageOps
from sklearn.decomposition import RandomizedPCA
from sklearn.externals import joblib
from os.path import join
import tempfile, numpy as np

def get_temp_filename():
    return join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()))

def open_image(filename):
    """
    """
    return Image.open(filename)

def pre_process_image(image, size=None):
    """
    """
    # convert to greyscale
    image = ImageOps.grayscale(image)

    # equalize histogram
    image = ImageOps.equalize(image)
    
    # resize to w x h
    if size:
        image = image.resize(size, Image.ANTIALIAS)

    return image

def get_nparray_from_img(filename, size=None):
    """
    """
    im = open_image(filename)
    im = pre_process_image(im, size)
    return np.asarray(im.getdata())

def get_model(n_components, data):
    pca = RandomizedPCA(n_components=n_components)
    pca.fit(data)
    return pca

def dump(obj, filename, compress_level):
    joblib.dump(obj, filename, compress=compress_level)

def load(filename):
    return joblib.load(filename)

