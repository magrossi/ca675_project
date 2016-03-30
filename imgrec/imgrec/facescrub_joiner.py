import sys, getopt, csv

def usage():
    print 'facescrub_joiner.py -m <actor file> -f <actress file> -o <output file>'

def main(argv):
    """
    Joines the FaceScrub actor and actresses dataset files into one where the id is unique per image.
    Command line example:
    python facescrub_joiner.py -m 'path/file_males_1.txt' -f 'path/file_females_2.txt' -o 'path/joined_file.txt'
    """
    input_files = []
    output_file = './face_dataset.txt'

    try:
        opts, args = getopt.getopt(argv, 'm:f:o:', ['file_male=', 'file_female=', 'output='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-m', '--file_male'):
            input_files.append(('m', arg))
        elif opt in ('-f', '--file_female'):
            input_files.append(('f', arg))
        elif opt in ('-o', '--output'):
            output_file = arg
        else:
            print 'invalid option = {}'.format(opt)
            usage()
            sys.exit(2)
    print input_files
    # name	image_id	face_id	url	bbox	sha256
    id = 0
    with open(output_file, 'wb') as fout:
        writer = csv.writer(fout, dialect='excel')
        writer.writerow(('id', 'name', 'gender', 'url', 'bbox', 'sha256', 'img_processed'))
        for gender, file in input_files:
            print '{} and {}'.format(gender, file)
            with open(file, 'rb') as fin:
                reader = csv.reader(fin, dialect='excel-tab')
                next(reader, None)  # skip the headers
                for name, imgid, faceid, url, bbox, sha256 in reader:
                    id += 1
                    dir = id/10000
                    subdir = id/100 - int(id/10000) * 100
                    writer.writerow((id, name, gender, url, bbox, sha256, '{}/{}/{}.bmp'.format(dir, subdir, id)))

    print ''
    print 'Saved {} entries to {} file.'.format(id, output_file)
    print ''

if __name__ == "__main__":
   main(sys.argv[1:])
