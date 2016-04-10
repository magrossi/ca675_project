#
docker exec -it ca675project_www_1 /usr/local/bin/python manage.py migrate

# Run seed
docker exec -it ca675project_www_1 /usr/local/bin/python seed.py


# Create the superuser
# docker exec -it ca675project_www_1 echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | /usr/local/bin/python manage.py shell
docker exec -it ca675project_www_1 /usr/local/bin/python manage.py createsuperuser --username root --email root@root.com

# db schell
docker exec -it ca675project_www_1 /usr/local/bin/python manage.py dbshell

# bash
docker exec -it ca675project_www_1 bash
docker exec -it ca675project_celery_1 bash


# python shell with django's context loaded
docker exec -it ca675project_www_1 /usr/local/bin/python manage.py shell

docker-compose down && docker-compose build && docker-compose up -d
docker exec -it ca675project_www_1 /usr/local/bin/python manage.py migrate && \
docker exec -it ca675project_www_1 /usr/local/bin/python seed.py && \
docker exec -it ca675project_www_1 /usr/local/bin/python build_datasets.py && \
docker exec -it ca675project_www_1 /usr/local/bin/python manage.py test

python manage.py makemigrations your_app_label

docker-compose run www /usr/local/bin/python manage.py test

##############


import os, django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from face_matcher.models import Face, Actor, History, HistoryItem
from django.contrib.auth.models import User
from face_matcher.tasks import find_similars

user = User.objects.get(username='demo')
face = user.face_set.first()

history = History.objects.create(user=user, in_face=face)
history.save()

r = find_similars.delay(history.id)
r.state
r.status

print 'Similarity results: {} [{}]'.format(history.status, history.output)
for item in history.historyitem_set.all():
  print '{}, {}'.format(item.face.id, item.similarity_score)

##############
import os, django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from face_matcher.models import Face, Actor, History, HistoryItem
from django.contrib.auth.models import User
from lib.findsimilars import FindSimilars

user = User.objects.get(username='demo')
face = user.face_set.first()

history = History.objects.create(user=user, in_face=face)
history.save()
FindSimilars.find(history)
print 'Similarity results: {} [{}]'.format(history.status, history.output)
for item in history.historyitem_set.all():
  print '{}, {}'.format(item.face.id, item.similarity_score)



To monitor celerys tasks/events
export TERM=linux
export TERMINFO=/etc/terminfo
/usr/local/bin/celery -A web events

  ENV TERM linux
  ENV TERMINFO /etc/terminfo
