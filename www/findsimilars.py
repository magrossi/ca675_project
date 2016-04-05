from mrjob.job import MRJob
from mrjob.job import MRStep
from scipy import spatial
from face_matcher.models import Face, History
from django.utils import timezone
import csv, StringIO, heapq, helpers, numpy as np

FACE_OPTION = '--new_eigenface'
MAX_RESULTS_OPTION = '--max_results'
FACE_SOURCE_FILTER = '--face_source_filter'
FACE_SOURCE_FILTER_OPTS = ['all', 'actor', 'user']
SIMILARITY_METHOD = '--similarity_method'
SIMILARITY_METHOD_OPTS = ['cosine', 'euclidean']

class FindSimilars():
    @classmethod
    def __get_eigenface_file_from_image(cls, image_file, bbox):
        model = helpers.load_model()
        im = helpers.get_nparray_from_img(image_file, bbox)
        eigenface = model.transform([im])
        eigenface_file = helpers.get_temp_filename()
        helpers.dump(eigenface, eigenface_file, compress_level=3)
        return eigenface_file

    @classmethod
    def find(cls, history, similarity_method='cosine', face_source_filter='all', max_results=10, job_options=['r', 'inline']):
        """
        """
        face_file = cls.__get_eigenface_file_from_image(history.in_face.full_face_path, history.in_face.bbox)

        # Build options for running the map reduce job
        opt = [FACE_OPTION, face_file,
               FACE_SOURCE_FILTER, face_source_filter,
               SIMILARITY_METHOD, similarity_method,
               MAX_RESULTS_OPTION, str(max_results)]

        # Add custom user options
        [opt.append(str(o)) for o in job_options]

        # Leave the input dataset for last
        opt.append('dataset.dat')

        # flag history as started
        history.status = history.RUNNING
        history.run_params = 'method={}, filter={}, max_results={}, options=[{}]'.format(
            similarity_method,
            face_source_filter,
            max_results,
            ', '.join(job_options)
        )
        history.save()

        # Call and run the job and output the key, value pairs
        job = FindSimilarsMapReduce(opt)
        try:
            with job.make_runner() as runner:
                runner.run()
                for line in runner.stream_output():
                    face_id, similarity_score = job.parse_output_line(line)
                    history.historyitem_set.create(face=Face.objects.get(pk=face_id), similarity_score = similarity_score)

                history.status = history.FINISHED
        except Exception as e:
            history.status = history.ERROR
            history.output = str(e)

        # save history object
        history.finished_at = timezone.now()
        history.save()

class FindSimilarsMapReduce(MRJob):
    """
    """

    def configure_options(self):
        super(FindSimilarsMapReduce, self).configure_options()
        self.add_file_option(FACE_OPTION)
        self.add_passthrough_option(MAX_RESULTS_OPTION, type='int', default=10)
        self.add_passthrough_option(FACE_SOURCE_FILTER, type='string', default='all')
        self.add_passthrough_option(SIMILARITY_METHOD, type='string', default='cosine')

    def load_options(self, args):
        super(FindSimilarsMapReduce, self).load_options(args)
        self.new_eigenface = helpers.load(getattr(self.options, FACE_OPTION[2:]))
        self.max_resutls = getattr(self.options, MAX_RESULTS_OPTION[2:])
        self.face_source_filter = getattr(self.options, FACE_SOURCE_FILTER[2:])
        self.similarity_method = getattr(self.options, SIMILARITY_METHOD[2:])

        if self.face_source_filter not in FACE_SOURCE_FILTER_OPTS:
            self.face_source_filter = 'all'

        if self.similarity_method not in SIMILARITY_METHOD_OPTS:
            self.similarity_method = 'cosine'

    def similarity(self, a, b):
        if self.similarity_method == 'euclidean':
            distance = np.linalg.norm(a-b)
            return 1 / (1 + distance)
        else:
            return 1 - spatial.distance.cosine(a, b)

    def can_use_source(self, source):
        return self.face_source_filter == 'all' or (self.face_source_filter == 'actor' and source == 'A') or (self.face_source_filter == 'user' and source == 'U')

    def mapper(self, _, line):
        """
        Reads a CSV entry with id, description and eigenface representation vector and
        computes the **eigenface** similary to the **new_eigenface** in a [0,1] interval
        where 0 is completely dissimilar and 1 is identical.
        The results are not ratio data, ie. 0.6 is not twice as similar than 0.3, the ratio can not
        be determined.
        """
        for face_id, face_source, eigenface_str in csv.reader(StringIO.StringIO(line)):
            if (self.can_use_source(face_source)):
                user_eigenface = np.asarray(map(float, eigenface_str.split()))
                yield None, (face_id, face_source, self.similarity(user_eigenface, self.new_eigenface))

    def combiner(self, _, user_similarities):
        """
        Trims the results to only the top **max_results** similar faces
        """
        most_similars = heapq.nlargest(self.max_resutls, user_similarities, key=lambda x: x[2])
        for face_id, face_source, similarity_score in most_similars:
            yield None, (face_id, face_source, similarity_score)

    def reducer(self, _, user_similarities):
        """
        Returns the **max_results** most similar faces
        """
        most_similars = heapq.nlargest(self.max_resutls, user_similarities, key=lambda x: x[2])
        for face_id, face_source, similarity_score in most_similars:
            yield face_id, similarity_score
