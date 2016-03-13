import sys, getopt
from os import path
from sklearn.externals import joblib
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from imgrec.findsimilars import FindSimilars
import imgrec.helpers

def main(argv):
    indataset = 'dataset.dat'
    inpca = 'model.dat'
    inimg = 'subject01.gif'
    outfile = 'test_similars.log'
    runner = 'inline'
    w = 320
    h = 243

    try:
        opts, args = getopt.getopt(argv, 'm:d:i:o:w:h:r:', ['model_file=',
            'dataset_file=', 'input_file=', 'output_file', 'width', 'height', 'runner'])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-m', '--model_file'):
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
        elif opt in ('-r', '--runner'):
            runner = arg
        else:
            usage()
            sys.exit(2)

    with open(outfile, 'w') as f:
        for k, v in FindSimilars.find(model_file=path.abspath(inpca),
            image_file=path.abspath(inimg),
            dataset=path.abspath(indataset),
            size=(w,h),
            job_options=['-r', runner]):
            line = '(k,v) = ({},{})'.format(k, v) 
            f.write(line)
            print line

    print ''
    print 'Results written to {}'.format(outfile)
    print ''

if __name__ == "__main__":
   main(sys.argv[1:])