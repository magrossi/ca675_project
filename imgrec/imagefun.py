from PIL import Image, ImageOps
import numpy as np

class ImageLoader:
    @classmethod
    def open_image(cls, filename):
        return Image.open(filename)

    @classmethod
    def pre_process_image(cls, image, size):
        width, height = size

        # convert to greyscale
        im = ImageOps.grayscale(im)

        # equalize histogram
        im = ImageOps.equalize(image)
        
        # resize to w x h
        im = im.resize((width,height), Image.ANTIALIAS)

        return im

    @classmethod
    def get_nparray_from_img(cls, filename, size):
        """
        """
        im = cls.open_image(filename)
        im = cls.pre_process_image(im, size)
        return np.asarray(im.getdata())
