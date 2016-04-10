from celery import shared_task
from lib.findsimilars import FindSimilars
from models import History

@shared_task
def find_similars(history_id, similarity_method='cosine', face_source_filter='all', max_results=10, job_options=['r', 'inline']):
    history = History.objects.get(id=history_id)
    FindSimilars.find(history, similarity_method=similarity_method, face_source_filter=face_source_filter, max_results=max_results, job_options=job_options)
