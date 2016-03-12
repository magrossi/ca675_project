from mrjob.job import MRJob
from mrjob.job import MRStep
from sklearn.externals import joblib
import csv, StringIO, heapq

FACE_OPTION = '--new_eigenface'
MAX_RESULTS_OPTION = '--max_results'

class FindSimilars():
    def get_unique_filename(prefix):
        return prefix + 'something_unique'

    @classmethod
    def find_similars(cls, model_file, face_file, dataset, size, n=10, job_options):
        """
        """
        # Build options for running the map reduce job
        opt = [FACE_OPTION, new_face_file,
               MAX_RESULTS_OPTION, model_file]

        # Add custom user options
        [opt.append(o) for o in job_options]
        
        # Leave the dataset for last
        opt.append(dataset)

        # Call and run the job and output the key, value pairs
        job = FindSimilarsMapReduce(opt)
        with mrjob.make_runner() as runner:
            runner.run()
            for line in runner.stream_output():
                key, value = mrjob.parse_output_line(line)
                yield key, value

class FindSimilarsMapReduce(MRJob):
        """       
        """
    def configure_options(self):
        super(FindSimilars,self).configure_options()
        self.add_file_option(FACE_OPTION)
        self.add_passthrough_option(MAX_RESULTS_OPTION, type='int', default=10)

    def load_options(self, args):
        super(FindSimilars, self).load_options(args)
        self.new_eigenface = self.load_file(self.options.new_eigenface)

    def load_file(self, filename):
        return joblib.load(filename)

    def normalize(self, value):
        """
        Normalizes a value in the 0 to infinity range to 0 to 1 range
        Used for turning a distance metric into a similarity metric
        The closest to 1 the more similar it is
        """
        return 1 / (1 + value)

    def distance(self, a, b):
        """
        Calculates the Euclidian Distance between **a** and **b**
        Resulting distance ranges from 0 to infinity
        """
        return np.linalg.norm(a-b)

    def mapper(self, _, line):
        for id, desc, eigenface_str in csv.reader(StringIO.StringIO(line)):
            user_eigenface = np.asarray(map(float, eigenface_str.split()))
            yield None, (id, desc, self.normalize(self.distance(user_eigenface, self.new_eigenface)))

    def reducer(self, _, user_distances):
        most_similars = heapq.nlargest(10, user_distances, key=lambda x: x[2])
        for id, desc, similarity in most_similars:
            yield id, (similarity, desc)

if __name__ == '__main__':
    FindSimilarsMapReduce.run()