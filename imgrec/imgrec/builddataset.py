import sys, getopt, helpers
from os import listdir
from os.path import isfile, join, basename

MODEL_FILE = 'model.dat'
DATASET_FILE = 'dataset.dat'

def main(argv):
    """
    Command line example:
    python builddataset.py -i 'img/dir' -o 'out/dir' -w <img width> -h <img height> -n <number of components for the model>
    """
    indir = '.\dataset'
    outdir = '.\output'
    w = 320
    h = 243
    nc = 150

    try:
        opts, args = getopt.getopt(argv, 'i:o:w:h:n:', ['img_dir=', 'out_dir=', 'width=', 'height=', 'n_components='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--height'):
            h = int(arg)
        elif opt in ('-w', '--width'):
            w = int(arg)
        elif opt in ('-o', '--out_dir'):
            outdir = arg
        elif opt in ('-i', '--img_dir'):
            indir = arg
        elif opt in ('-n', '--n_components'):
            nc = int(arg)
        else:
            usage()
            sys.exit(2)

    files = [join(indir, f) for f in listdir(indir) if isfile(join(indir, f))]
    data = list()
    data_labels = list()
    for file in files:
        data.append(helpers.get_nparray_from_img(file, (w, h)))
        data_labels.append(basename(file)) # temporary while we do not have more info

    model = helpers.get_model(n_components=nc, data=data)    
    helpers.dump(model, join(outdir, MODEL_FILE), compress_level=3)

    with open(join(outdir, DATASET_FILE), 'wb') as f:
        for index, eigenface in enumerate(model.transform(data)):
            f.write('"{}","{}","{}"\n'.format(index, data_labels[index], ' '.join(map(str, eigenface))))

    print ''
    print 'Created {} and {} in directory {}.'.format(MODEL_FILE, DATASET_FILE, outdir)
    print 'PCA Explained Variance Ratio: {}'.format(sum(model.explained_variance_ratio_))
    print 'Obs.: if this number is not satisfactory try increasing the number of components'
    print ''

if __name__ == "__main__":
   main(sys.argv[1:])