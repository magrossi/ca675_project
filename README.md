## CA675 Group Project

TODO - description

### Bootstrapping

1. Start new machine - `docker-machine create -d virtualbox dev;`
1. Build images - `docker-compose build`
1. Start services - `docker-compose up -d`
1. Create migrations - `docker-compose run web /usr/local/bin/python manage.py migrate`
1. Add an admin user - `docker-compose run web /usr/local/bin/python manage.py createsuperuser --username root --email root@root.com`
1. Grab IP - `docker-machine ip dev` - and view in your browser
