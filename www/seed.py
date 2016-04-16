import os
import sys
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from face_matcher.tasks import seed


def seed_tables():
    # If called directly (without the .delay() method) the task will execute
    # Asynchronously as if it were not a celery task
    users_ct, actor_ct, faces_ct = seed(max_faces=settings.FACEREC_MAX_SEED_IMG)

    print ''
    print 'Seed Summary:'
    print '   Users  {}'.format(users_ct)
    print '  Actors  {}'.format(actor_ct)
    print '   Faces  {}'.format(faces_ct)
    print ''


def main(argv):
    seed_tables()

if __name__ == '__main__':
    main(sys.argv[1:])
