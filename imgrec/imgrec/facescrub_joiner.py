import sys, getopt, csv

def main(argv):
    """
    Joines the FaceScrub actor and actresses dataset files into one where the id is unique per image.
    Command line example:
    python facescrub_joiner.py -f 'path/file_1.txt' -f 'path/file_2.txt' -o 'path/joined_file.txt'
    """
    input_files = []
    output_file = './face_dataset.txt'

    try:
        opts, args = getopt.getopt(argv, 'f:o:', ['file=', 'output='])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-f', '--file'):
            input_files.append(arg)
        elif opt in ('-o', '--output'):
            output_file = arg
        else:
            usage()
            sys.exit(2)

    # name	image_id	face_id	url	bbox	sha256
    id = 0
    with open(output_file, 'wb') as fout:
        writer = csv.writer(fout, dialect='excel')
        writer.writerow(('id', 'name', 'url', 'bbox', 'sha256', 'img_processed'))
        for file in input_files:
            with open(file, 'rb') as fin:
                reader = csv.reader(fin, dialect='excel-tab')
                next(reader, None)  # skip the headers
                for name, imgid, faceid, url, bbox, sha256 in reader:
                    id += 1
                    dir = id/10000
                    subdir = id/100 - int(id/10000) * 100
                    writer.writerow((id, name, url, bbox, sha256, '{}/{}/{}.bmp'.format(dir, subdir, id)))

    print ''
    print 'Saved {} entries to {} file.'.format(id, output_file)
    print ''

if __name__ == "__main__":
   main(sys.argv[1:])
