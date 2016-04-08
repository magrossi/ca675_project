# CA675 Group Project ![Build status](https://circleci.com/gh/magrossi/ca675_project.svg?style=shield)

TODO - description

### Bootstrapping

1. Install the latest docker toolkit, `open https://github.com/docker/toolbox/releases/tag/v1.10.3`
1. Create a machine, `docker-machine create -d virtualbox --virtualbox-memory 4096 --virtualbox-cpu-count "2" dev`
1. Start and point to the instance, `docker-machine start dev && eval $(docker-machine env dev)`
1. Build the images and start the services, `docker-compose build && docker-compose up -d && docker-compose logs`
1. Create migrations (from www), `docker-compose run www /usr/local/bin/python manage.py migrate`
1. Add an admin user (from www), `docker-compose run www /usr/local/bin/python manage.py createsuperuser --username root --email root@root.com`
1. Seed the database (from www), `docker-compose run www /usr/local/bin/python seed.py`
1. Create the working model/face dataset files (from wwww), `docker-compose run www /usr/local/bin/python build_datasets.py`
1. Grab the IP, `docker-machine ip dev`, and view in your browser

### Running Tests Locally

1. Build the images, `docker-compose build`
2. Run the tests, `docker-compose run www /usr/local/bin/python manage.py test`

### Running migrations

1. Upon making model DDL changes (from www), `docker-compose run www /usr/local/bin/python manage.py makemigrations face_matcher`
1. Then run the new migration (from www), `docker-compose run www /usr/local/bin/python manage.py migrate`

### Running the REPL

Simply run (from www) `docker-compose run www /usr/local/bin/python manage.py shell`
```
Python 2.7.11 (default, Mar 19 2016, 01:05:53)
[GCC 4.9.2] on linux2
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from face_matcher.models import Upload
>>> Upload.objects.all()
[]
```

### Running the Psql shell

Simply run (from www) `docker-compose run www /usr/local/bin/python manage.py dbshell`
```
psql (9.4.6, server 9.5.1)
WARNING: psql major version 9.4, server major version 9.5.
         Some psql features might not work.
Type "help" for help.

postgres=# \d
                        List of relations
 Schema |               Name                |   Type   |  Owner
--------+-----------------------------------+----------+----------
 public | auth_group                        | table    | postgres
 public | auth_group_id_seq                 | sequence | postgres
 public | auth_group_permissions            | table    | postgres
 public | auth_group_permissions_id_seq     | sequence | postgres
 public | auth_permission                   | table    | postgres
 public | auth_permission_id_seq            | sequence | postgres
 public | auth_user                         | table    | postgres
 public | auth_user_groups                  | table    | postgres
 public | auth_user_groups_id_seq           | sequence | postgres
 public | auth_user_id_seq                  | sequence | postgres
 public | auth_user_user_permissions        | table    | postgres
 public | auth_user_user_permissions_id_seq | sequence | postgres
 public | django_admin_log                  | table    | postgres
 public | django_admin_log_id_seq           | sequence | postgres
 public | django_content_type               | table    | postgres
 public | django_content_type_id_seq        | sequence | postgres
 public | django_migrations                 | table    | postgres
 public | django_migrations_id_seq          | sequence | postgres
 public | django_session                    | table    | postgres
 public | face_matcher_upload               | table    | postgres
 public | face_matcher_upload_id_seq        | sequence | postgres
(21 rows)
```

### Example for searching similar faces

The below is a sample Python script that will use the app to search for similar faces (when the UI is done we can use the same code to submit our searches).

This script takes advantage of the `demo` user that is created in the seed.py script and will return the 10 most similar faces alongside their similarity score. The higher the score, the more similar the faces are.

The `FindSimilars.find()` function accepts some parameters besides just the `history` object:

```
find(history, similarity_method='cosine', face_source_filter='all', max_results=10, job_options=['r', 'inline'])
```

* `similarity_method=` defines which similarity function will be used. Possible functions are `cosine` (score ranges from -1,1) and `euclidean` (from 0,1). The returned faces may vary depending on the function used (but not by that much!).
* `face_source_filter=` will filter the search depending on the source of the face image, `actor` will only look for images of actors, `user` only for user images and `all` will look for similarity between all images.
* `max_results=` defines the number of similar faces returned
* `job_options=` will simply forward the parameters to the `MrJob` map reduce framework. This allows us to change where the job will be run. If we want to run this in EMR for example we can pass `['r', 'emr']` as parameters. The default is `['r', 'inline']` which is ideal for running the job locally. Please refer to https://pythonhosted.org/mrjob/ for specific options available.

```
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
```
