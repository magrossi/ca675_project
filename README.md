# CA675 Group Project ![Build status](https://circleci.com/gh/magrossi/ca675_project.svg?style=shield)

Similar face image finder app built in Python, Django, Postgres and Nginx in a containerized microservices environment.

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

### Searching similar faces
The below are sample Python scripts that will use the app to search for similar faces `synchronously` and `asynchronously`. The synchronous method IS NOT suitable for running from the UI code as it will block the web service from responding until the search is completed (might take some time). For invoking searches from the UI use the asynchronous verion.

This scripts takes advantage of the `demo` user that is created in the seed.py script and will return the 10 most similar faces alongside their similarity score. The higher the score, the more similar the faces are.
##### Synchronously (use only for tests)
The `FindSimilars.find()` function accepts some parameters besides just the `history` object:

```
find(history, similarity_method='cosine', face_source_filter='all', max_results=10, job_options=['r', 'inline'])
```
* `history` is a History model instance. It is important that it has already been saved (with a valid id).
* `similarity_method=` defines which similarity function will be used. Possible functions are `cosine` (score ranges from -1,1) and `euclidean` (from 0,1). The returned faces may vary depending on the function used (but not by that much!).
* `face_source_filter=` will filter the search depending on the source of the face image, `actor` will only look for images of actors, `user` only for user images and `all` will look for similarity between all images.
* `max_results=` defines the number of similar faces returned
* `job_options=` will simply forward the parameters to the `MrJob` map reduce framework. This allows us to change where the job will be run. If we want to run this in EMR for example we can pass `['r', 'emr']` as parameters. The default is `['r', 'inline']` which is ideal for running the job locally. Please refer to https://pythonhosted.org/mrjob/ for specific options available.

First run the Python shell on the `www` service by executing `docker-compose run www /usr/local/bin/python manage.py shell`. In the python shell that openes execute the code below:
```
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
##### Asynchronously
For running this code in a separate process (in fact it will run in an entirely different container) use the wrapper task function tasks.find_similars.delay(). The parameters are almost the same as the synchronous version with the exception of the `history` object instance has now been replaced with a `history_id` with the `PK` of the `History` model instance.

```
find_similars(history_id, similarity_method='cosine', face_source_filter='all', max_results=10, job_options=['r', 'inline'])
```
* `history_id` is the primary key of the History model instance.
* `...` the remaining parameters are the same as the synchronous call (please refer to the above sub-section for details).

To execute in asynchronous mode open the Python shell like before and run the script:
```
from face_matcher.models import Face, Actor, History, HistoryItem
from django.contrib.auth.models import User
from face_matcher.tasks import find_similars

user = User.objects.get(username='demo')
face = user.face_set.first()

history = History.objects.create(user=user, in_face=face)
history.save()

r = find_similars.delay(history.id)
# You can monitor the execution of the task by acessing either:
# r.state or r.status
# Once done you will have to reload the history object as it was modified outside the scope of this thread
history.refresh_from_db()
print 'Similarity results: {} [{}]'.format(history.status, history.output)
for item in history.historyitem_set.all():
  print '{}, {}'.format(item.face.id, item.similarity_score)
```
You can also have a function that runs on a heartbeat that refreshes the submitted `History` model instance and checks for its `status`.
```
history.refresh_from_db()
if history.status in [History.FINISHED, History.ERROR]:
    print 'Finished with status: {}'.format(history.status)
```
Possible statuses are:
* `History.PENDING`
* `History.RUNNING`
* `History.FINISHED`
* `History.ERROR`

### Deploying to AWS

One can provision the application stack to an Ec2 instance through the following steps:
1. Install and configure the AWS CLI under one of your IAM users in your chosen region, https://aws.amazon.com/cli/
1. Create a VPC for the Ec2 instnace and take note of its ID, http://docs.aws.amazon.com/cli/latest/reference/ec2/create-vpc.html
1. Create a subnet for the VPC and take note of the AZ it was created under, http://docs.aws.amazon.com/cli/latest/reference/ec2/create-subnet.html
1. Along with the desired instance name, supply the VPC id and subnet's zone to the provisioning script: `NAME=fm-aws VPC_ID=someId ZONE=subnetZoneLetter REGION=someRegion sh deploy.sh -p`
1. In your Ec2 console you will notice that the according instance has been provisioned under a new 'docker-machine' security group. This group's inbound traffic rules should be updated to allow the traffic types HTTP, PostgreSQL and SSH from all sources, http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html#adding-security-group-rule
1. Under your RDS console, create a Postgres "Dev/Test" instance type using the 9.4.7 engine in a db.t2.micro machine while taking note of the DB identifier, username and password. The instance set up should create new VPC, subnet and security group while being publicly accessible, http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_GettingStarted.CreatingConnecting.PostgreSQL.html#CHAP_GettingStarted.Creating.PostgreSQL
1. When the RDS instance is created take note of its endpoint and create a .env_prod file in the following format:
```
  DJANGO_ENV=production
  SECRET_KEY={{some_SHA}}
  DB_NAME={{name}}
  DB_USER={{user}}
  DB_PASS={{pass}}
  DB_SERVICE={{RDS_endpoint}}
  DB_PORT={{port}}
```

One can deploy the application through the following steps:
1. Simply run the deploy script, `NAME=aws-fm sh deploy.sh`
1. Preview the deployed application, `open http://$(docker-machine ip aws-fm-med)`
