import sys, getopt, numpy as np
from os import listdir
from os.path import isfile, join
from sklearn.decomposition import RandomizedPCA
from sklearn.externals import joblib
from image_loader import ImageLoader
import pickle

def main(argv):
    indir = '.\dataset'
    outdir = '.\output'
    w = 320
    h = 243
    nc = 150

    try:
        opts, args = getopt.getopt(argv, 'i:o:whn', ['img_dir=', 'out_dir=', 'width=', 'height=', 'n_components='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--height'):
            h = arg
        elif opt in ('-w', '--width'):
            w = arg
        elif opt in ('-o', '--out_dir'):
            outdir = arg
        elif opt in ('-i', '--img_dir'):
            indir = arg
        elif opt in ('-n', '--n_components'):
            indir = arg
        else:
            usage()
            sys.exit(2)

    files = [join(indir, f) for f in listdir(indir) if isfile(join(indir, f))]
    data = list()
    data_labels = list()
    for file in files:
        data.append(ImageLoader.get_nparray_from_img(file, w, h))
        data_labels.append(file)

    pca = RandomizedPCA(n_components=nc) # number of components
    pca.fit(data)

    joblib.dump(pca, join(outdir, 'pca.dumps'), compress=3) # compress level from 0 to 9

    with open(join(outdir, 'eigenfaces.dumps'), 'wb') as f:
        for index, eigenface in enumerate(pca.transform(data)):
            f.write('"{}","{}","{}"\n'.format(index, data_labels[index], ' '.join(map(str, eigenface))))

    print 'Created pca.dumps and eigenfaces.dumps in directory {}.'.format(outdir)
    print 'PCA Explained Variance Ratio: {}'.format(sum(pca.explained_variance_ratio_))

if __name__ == "__main__":
   main(sys.argv[1:])