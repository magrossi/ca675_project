FROM python:2.7-onbuild
RUN apt-get update && apt-get -y install postgresql-client
ADD . /usr/src/app
WORKDIR /usr/src/app
VOLUME /usr/src/app
CMD /usr/local/bin/gunicorn web.wsgi:application -w 2 -b :8000 --reload
