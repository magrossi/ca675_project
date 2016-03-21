from mrjob.job import MRJob
from mrjob.job import MRStep
import csv, StringIO, heapq, helpers, numpy as np

FACE_OPTION = '--new_eigenface'
MAX_RESULTS_OPTION = '--max_results'

class FindSimilars():
    @classmethod
    def __get_eigenface_file_from_image(cls, model_file, image_file, size):
        model = helpers.load(model_file)
        im = helpers.get_nparray_from_img(image_file, size)
        eigenface = model.transform([im])
        eigenface_file = helpers.get_temp_filename()
        helpers.dump(eigenface, eigenface_file, compress_level=3)
        return eigenface_file

    @classmethod
    def find(cls, model_file, image_file, dataset, size=None, max_results=10, job_options=['r', 'inline']):
        """
        """
        face_file = cls.__get_eigenface_file_from_image(model_file, image_file, size)

        # Build options for running the map reduce job
        opt = [FACE_OPTION, face_file,
               MAX_RESULTS_OPTION, str(max_results)]

        # Add custom user options
        [opt.append(str(o)) for o in job_options]
        
        # Leave the input dataset for last
        opt.append(dataset)

        # Call and run the job and output the key, value pairs
        job = FindSimilarsMapReduce(opt)
        with job.make_runner() as runner:
            runner.run()
            for line in runner.stream_output():
                key, value = job.parse_output_line(line)
                yield key, value

class FindSimilarsMapReduce(MRJob):
    """       
    """

    def configure_options(self):
        super(FindSimilarsMapReduce, self).configure_options()
        self.add_file_option(FACE_OPTION)
        self.add_passthrough_option(MAX_RESULTS_OPTION, type='int', default=10)

    def load_options(self, args):
        super(FindSimilarsMapReduce, self).load_options(args)
        self.new_eigenface = helpers.load(getattr(self.options, FACE_OPTION[2:]))
        self.max_resutls = getattr(self.options, MAX_RESULTS_OPTION[2:])

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
        """
        Reads a CSV entry with id, description and eigenface representation vector and
        computes the **eigenface** similary to the **new_eigenface** in a [0,1] interval
        where 0 is completely dissimilar and 1 is identical.
        The results are not ratio data, ie. 0.6 is not twice as similar than 0.3, the ratio can not
        be determined.
        """
        for id, desc, eigenface_str in csv.reader(StringIO.StringIO(line)):
            user_eigenface = np.asarray(map(float, eigenface_str.split()))
            yield None, (id, desc, self.distance(user_eigenface, self.new_eigenface))

    def combiner(self, _, user_similarities):
        """
        Trims the results to only the top **max_results** similar faces
        """
        most_similars = heapq.nlargest(self.max_resutls, user_similarities, key=lambda x: x[2])
        for id, desc, similarity in most_similars:
            yield None, (id, desc, similarity)

    def reducer(self, _, user_similarities):
        """
        Returns the **max_results** most similar faces
        """
        most_similars = heapq.nlargest(self.max_resutls, user_similarities, key=lambda x: x[2])
        for id, desc, similarity in most_similars:
            yield id, (desc, similarity)

if __name__ == '__main__':
    FindSimilarsMapReduce.run()