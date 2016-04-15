from PIL import Image, ImageOps
from sklearn.decomposition import RandomizedPCA, IncrementalPCA
from sklearn.externals import joblib
from django.conf import settings
from simples3 import S3Bucket
from StringIO import StringIO
from itertools import chain, islice
from lock import RedisReaderLock, RedisWriterLock
import os, os.path, redis, numpy as np

class MetaModelBuilder(type):
    @property
    def model_filename(cls):
        return cls._model_filename

    @property
    def dataset_filename(cls):
        return cls._dataset_filename

class ModelBuilder():
    __metaclass__ = MetaModelBuilder

    _model_filename = 'model.dat'
    _dataset_filename = 'dataset.dat'

    @classmethod
    def build(cls, dataset):
        pca = RandomizedPCA(n_components=ImageLibrary.components)
        pca.fit(dataset)
        eigenfaces = pca.transform(dataset)
        return (pca, eigenfaces)

    @classmethod
    def build_from_iter(cls, data_gen, chunk_size):
        pca = IncrementalPCA(n_components=ImageLibrary.components)
        for chunk in cls._chunks(data_gen, size=chunk_size):
            data = cls._array_from_iter(chunk, dtype=np.uint8)
            pca.partial_fit(data)
        return pca

    @classmethod
    def apply_from_iter(cls, model, img_data_gen):
        for img_data in img_data_gen:
            yield model.transform([img_data])[0]

    @classmethod
    def apply(cls, img_data):
        model = cls.load()
        return model.transform([img_data])[0]

    @classmethod
    def dump(cls, model):
        with RedisWriterLock(cls._get_redis(), cls.model_filename):
            joblib.dump(model, cls.model_filename, compress=3)

    @classmethod
    def load(cls):
        with RedisReaderLock(cls._get_redis(), cls.model_filename):
            return joblib.load(cls.model_filename)

    @classmethod
    def dump_eigenface(cls, eigenface, filename):
        joblib.dump(eigenface, filename, compress=3)

    @classmethod
    def load_eigenface(cls, filename):
        return joblib.load(filename)

    @classmethod
    def lock_dataset_for_read(cls):
        return RedisReaderLock(cls._get_redis(), cls.dataset_filename)

    @classmethod
    def dump_dataset(cls, eigenfaces, data_labels):
        # create and save the dataset of eigenfaces by projecting the processed
        # image data into an orthogonal plane using the fitted model
        with RedisWriterLock(cls._get_redis(), cls.dataset_filename):
            with open(cls.dataset_filename, 'wb') as f:
                for index, eigenface in enumerate(eigenfaces):
                    face_id, face_source = data_labels[index]
                    f.write('"{}","{}","{}"\n'.format(face_id, face_source, cls.eigenface_to_str(eigenface)))

    @classmethod
    def append_dataset(cls, eigenface, data_label):
        # append to the existing dataset the eigenface and associated data_label
        with RedisWriterLock(cls._get_redis(), cls.dataset_filename):
            with open(cls.dataset_filename, 'a') as f:
                face_id, face_source = data_label
                f.write('"{}","{}","{}"\n'.format(face_id, face_source, cls.eigenface_to_str(eigenface)))

    @classmethod
    def eigenface_to_str(cls, eigenface):
        return ' '.join(map(str, eigenface))

    @classmethod
    def str_to_eigenface(cls, eigenstr):
        return np.asarray(map(float, eigenstr.split()))

    @classmethod
    def _chunks(cls, iterable, size=10):
        iterator = iter(iterable)
        for first in iterator:
            yield chain([first], islice(iterator, size - 1))

    @classmethod
    def _array_from_iter(cls, it, dtype=None):
        try:
            ans = np.array([it.next()], dtype=dtype)
        except StopIteration:
            raise ValueError('iterator contains 0 items')
        shape0 = ans.shape[1:]
        for (i, x) in enumerate(it):
            ans.resize((i+2,)+shape0)
            ans[i+1] = x
        return ans

    @classmethod
    def _get_redis(cls):
        return redis.Redis(settings.REDIS_HOST)

class MetaImageLibrary(type):
    @property
    def size(cls):
        return settings.FACEREC_IMG_SIZE

    @property
    def components(cls):
        return settings.FACEREC_COMPONENTS

class ImageLibrary():
    __metaclass__ = MetaImageLibrary

    BASE_S3_URL = 'http://{}.s3.amazonaws.com'.format(settings.IMAGE_STORAGE_S3_BUCKET)

    _LOCAL_STORAGE = 'local'
    _S3_STORAGE = 's3'

    @classmethod
    def get_image_url(cls, rel_img_path):
        if settings.IMAGE_STORAGE_MODE == cls._LOCAL_STORAGE:
            return os.path.join(settings.STATIC_URL, 'images', rel_img_path)
        return '{}/{}{}'.format(cls.BASE_S3_URL, settings.IMAGE_STORAGE_S3_PREFIX, rel_img_path)

    @classmethod
    def save_image(cls, raw_img, rel_img_path):
        if settings.IMAGE_STORAGE_MODE == cls._LOCAL_STORAGE:
            filename = cls.get_image_url(rel_img_path)
            full_dir = os.path.dirname(filename)
            if not os.path.exists(full_dir):
                os.makedirs(full_dir)
            with open(filename, 'wb') as f:
                f.write(raw_img)
        else:
            cls._get_s3bucket().put(settings.IMAGE_STORAGE_S3_PREFIX + rel_img_path, raw_img)

    @classmethod
    def del_image(cls, rel_img_path):
        if settings.IMAGE_STORAGE_MODE == cls._LOCAL_STORAGE:
            filename = os.path.join(settings.IMAGE_STORAGE_LOCAL_DIR, rel_img_path)
            if os.path.isfile(filename):
                os.remove(filename)
        else:
            filename = settings.IMAGE_STORAGE_S3_PREFIX + rel_img_path
            s3 = cls._get_s3bucket()
            if filename in s3:
                s3.delete(filename)

    @classmethod
    def process_image(cls, img_path, bbox):
        return list(cls.process_images([(img_path, bbox)]))[0]

    @classmethod
    def process_images(cls, image_bbox_list):
        if settings.IMAGE_STORAGE_MODE == cls._LOCAL_STORAGE:
            return cls._process_images_local(image_bbox_list)
        else:
            return cls._process_images_s3(image_bbox_list)

    @classmethod
    def list_all(cls):
        if settings.IMAGE_STORAGE_MODE == cls._LOCAL_STORAGE:
            for path, subdirs, files in os.walk(settings.IMAGE_STORAGE_LOCAL_DIR):
                for name in files:
                    yield os.path.relpath(os.path.join(path, name), settings.IMAGE_STORAGE_LOCAL_DIR)
        else:
            s3 = cls._get_s3bucket()
            for (key, modify, etag, size) in s3.listdir(prefix=settings.IMAGE_STORAGE_S3_PREFIX):
                yield os.path.relpath(key, settings.IMAGE_STORAGE_S3_PREFIX)

    @classmethod
    def _get_s3bucket(cls):
        return S3Bucket(settings.IMAGE_STORAGE_S3_BUCKET,
                        access_key=settings.IMAGE_STORAGE_S3_ACCESS_KEY,
                        secret_key=settings.IMAGE_STORAGE_S3_SECRET_KEY,
                        base_url=cls.BASE_S3_URL)

    @classmethod
    def _pre_process_image(cls, image, bbox):
        """
        image is a PIL.Image
        bbox is x0,y0,x1,y1
        """
        # crop face if not already done so
        x0, y0, x1, y1 = bbox
        curr_width, curr_height = image.size

        if x1 <= curr_width and y1 <= curr_height:
            image = image.crop(bbox)

        image = ImageOps.grayscale(image) # convert to greyscale
        image = image.resize(cls.size, Image.ANTIALIAS) # resize to working size
        image = ImageOps.equalize(image) # equalize histogram

        return np.asarray(image.getdata())

    @classmethod
    def _process_images_local(cls, image_bbox_list):
        for img_path, bbox in image_bbox_list:
            image = Image.open(os.path.join(settings.IMAGE_STORAGE_LOCAL_DIR, img_path))
            yield cls._pre_process_image(image, bbox)

    @classmethod
    def _process_images_s3(cls, image_bbox_list):
        s3 = cls._get_s3bucket()
        for img_path, bbox in image_bbox_list:
            raw_img = s3.get(settings.IMAGE_STORAGE_S3_PREFIX + img_path).read()
            image = Image.open(StringIO(raw_img))
            yield cls._pre_process_image(image, bbox)
