import sys, getopt, csv, time, hashlib, urllib2, helpers
from StringIO import StringIO
from joblib import Parallel, delayed
from os import makedirs, remove
from os.path import join, isfile, abspath, exists, dirname
from PIL import Image

def proc_item(item):
    """
    Processes one item in the dataset (one face)
    """
    retry, url, bbox, sha256, local_img = item
    failed_img_file = local_img + '.failed'

    # Check if already tried to download this image (only retry if flag specified)
    if isfile(local_img) or (isfile(failed_img_file) and not retry):
        return

    if isfile(failed_img_file):
        remove(failed_img_file)

    # Create directory tree if not existing
    if not exists(dirname(local_img)):
        try:
            makedirs(dirname(local_img))
        except:
            pass # ignore if exists (race condition)

    # Download and process image
    try:
        # Download full image to disk
        img_raw = urllib2.urlopen(url, timeout=5).read()
        # Fail if image hash does not match
        calc_sha256 = hashlib.sha256(img_raw).hexdigest()
        if calc_sha256 != sha256:
            #remove(local_img) # remove corrupted image
            raise Exception('sha256 mismatch')
        # Process image
        img = Image.open(StringIO(img_raw)).crop(bbox)
        # Removed image preprocessing in favor for doing it at a later stage
        # img = helpers.pre_process_image(img, size=(100,100))
        img.save(local_img)
    except Exception as e:
        with open(failed_img_file, 'a') as err:
            err.write(str(e))
            err.close() # create failed file

def usage():
    print ''
    print 'Usage example:'
    print 'python facescrub_downloader.py -r -d path/to/facescrub_dataset.txt -p path/to/images/ -n 50'
    print 'Use -r to retry previously failed images and -n to determine the number of jobs.'
    print ''

def main(argv):
    """
    Reads processed facescrub dataset and saved down pre-processed face images
    Command line example:
    python facescrub_downloader.py -r -d 'path/facescrub_dataset.txt' -p 'path/to/images/' -n 100
    """
    dataset_file = './face_dataset.txt'
    img_path = './images'
    jobs = 50
    retry = False

    try:
        opts, args = getopt.getopt(argv, 'd:p:n:r', ['dataset=', 'image_path=', 'jobs=', 'retry'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-d', '--dataset'):
            dataset_file = arg
        elif opt in ('-p', '--image_path'):
            img_path = arg
        elif opt in ('-n', '--jobs'):
            jobs = int(arg)
        elif opt in ('-r', '--retry'):
            retry = True
        else:
            usage()
            sys.exit(2)

    start = time.time()
    # 'id', 'name', 'gender', 'url', 'bbox', 'sha256', 'img_processed'
    with open(dataset_file, 'rb') as dset:
        reader = csv.reader(dset, dialect='excel')
        next(reader, None)  # skip the headers
        # Downloads files in parallel up to 'jobs' concurrently
        Parallel(n_jobs=jobs)(delayed(proc_item)((retry, url, map(lambda s: int(s), bbox.split(',')), sha256, abspath(join(img_path, local_img))))
            for id, name, gender, url, bbox, sha256, local_img in reader)

        # Sequential mode for debug
        #count = len([proc_item((url, map(lambda s: int(s), bbox.split(',')), sha256, abspath(join(img_path, local_img))))
        #    for id, name, gender, url, bbox, sha256, local_img in reader])
    end = time.time()

    print ''
    print 'Downloaded {} images in {} seconds.'.format(count, end-start)
    print ''

if __name__ == "__main__":
    main(sys.argv[1:])
