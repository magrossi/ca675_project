## CA675 Group Project

TODO - description

### Bootstrapping

1. Install the latest docker toolkit, `open https://github.com/docker/toolbox/releases/tag/v1.10.3`
1. Create a machine, `docker-machine create -d virtualbox --virtualbox-memory 4096 --virtualbox-cpu-count "2" dev`
1. Start and point to the instance, `docker-machine start dev && eval $(docker-machine env dev)`
1. Build the images and start the services, `docker-compose build && docker-compose up -d && docker-compose logs`
1. Create migrations (from www), `docker-compose run www /usr/local/bin/python manage.py migrate`
1. Add an admin user (from www), `docker-compose run www /usr/local/bin/python manage.py createsuperuser --username root --email root@root.com`
1. Seed the database (from www), `docker-compose run www /usr/local/bin/python seed.py`
1. Grab the IP, `docker-machine ip dev`, and view in your browser

### Running migrations

1. Upon making model DDL changes (from www), `docker-compose run www /usr/local/bin/python manage.py makemigrations face_matcher`
1. Then run the new migration (from www), `docker-compose run www /usr/local/bin/python manage.py migrate`

## Running the REPL

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

## Running the Psql shell

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
