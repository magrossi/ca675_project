import sys, getopt, os
from sklearn.externals import joblib
from find_similars import FindSimilars
from image_loader import ImageLoader

def main(argv):
    indataset = 'eigenfaces.dumps'
    inpca = 'pca.dumps'
    inimg = 'subject01.gif'
    outfile = 'out.log'
    w = 320
    h = 243

    try:
        opts, args = getopt.getopt(argv, 'p:d:i:o:w:h:', ['pca_file=', 'dataset_file=', 'input_file='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-p', '--pca_file'):
            inpca = arg
        elif opt in ('-d', '--dataset_file'):
            indataset = arg
        elif opt in ('-i', '--input_file'):
            inimg = arg
        elif opt in ('-o', '--output_file'):
            outfile = arg
        elif opt in ('-w', '--width'):
            w = arg
        elif opt in ('-h', '--height'):
            h = arg
        else:
            usage()
            sys.exit(2)

    eigenface = pca.transform(ImageLoader.get_nparray_from_img(inimg, w, h))
    joblib.dump(eigenface, 'new_eigenface.dumps', compress=3) # save to file and pass it on to mrjob

    for k, v in FindSimilars.find_similars(os.path.abspath(inpca), os.path.abspath('new_eigenface.dumps'), os.path.abspath(indataset), size=(50,50), ['-r', 'inline']):
        print 'k, v = {}, {}'.format(key, value)

if __name__ == "__main__":
   main(sys.argv[1:])