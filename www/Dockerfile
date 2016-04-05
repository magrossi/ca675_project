FROM buildpack-deps:jessie

### Linux deps
RUN set -ex \
  && apt-get update \
  && apt-get install -y postgresql-client libblas-dev liblapack-dev libatlas-base-dev gfortran \
  && apt-get purge -y python.*


### Python deps
ENV LANG C.UTF-8
ENV GPG_KEY C01E1CAD5EA2C4F0B8E3571504C367C218ADD4FF
ENV PYTHON_VERSION 2.7.11
ENV PYTHON_PIP_VERSION 8.1.1

RUN set -ex \
  && curl -fSL "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz" -o python.tar.xz \
  && curl -fSL "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc" -o python.tar.xz.asc \
  && export GNUPGHOME="$(mktemp -d)" \
  && gpg --keyserver ha.pool.sks-keyservers.net --recv-keys "$GPG_KEY" \
  && gpg --batch --verify python.tar.xz.asc python.tar.xz \
  && rm -r "$GNUPGHOME" python.tar.xz.asc \
  && mkdir -p /usr/src/python \
  && tar -xJC /usr/src/python --strip-components=1 -f python.tar.xz \
  && rm python.tar.xz \
  \
  && cd /usr/src/python \
  && ./configure --enable-shared --enable-unicode=ucs4 \
  && make -j$(nproc) \
  && make install \
  && ldconfig \
  && curl -fSL 'https://bootstrap.pypa.io/get-pip.py' | python2 \
  && pip install --no-cache-dir --upgrade pip==$PYTHON_PIP_VERSION \
  && find /usr/local \
    \( -type d -a -name test -o -name tests \) \
    -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
    -exec rm -rf '{}' + \
  && rm -rf /usr/src/python

RUN pip install --no-cache-dir virtualenv

### App
ENV FACEREC_WIDTH 100
ENV FACEREC_HEIGHT 100
ENV FACEREC_COMPONENTS 150
ENV WORKDIR /usr/src/app
ENV IMG_BASE_DIR /usr/src/app/static/images
RUN mkdir -p $WORKDIR
WORKDIR $WORKDIR
VOLUME $WORKDIR

COPY requirements.txt $WORKDIR
RUN pip install --no-cache-dir -r requirements.txt
COPY . $WORKDIR

### Fetch datasets from Google Drive
#ENV FACESCRUB_DATASET_ZIP_DRIVE_ID 0Bzt4aP7vYnOTaENxWVFCQ0kwRkU
#RUN wget --no-check-certificate https://googledrive.com/host/$FACESCRUB_DATASET_ZIP_DRIVE_ID -O /tmp/facescrub_dataset.tar.gz #&& \
#    tar xvf /tmp/facescrub_dataset.tar.gz -C $WORKDIR && \
#    rm /tmp/facescrub_dataset.tar.gz
#ADD https://googledrive.com/host/$FACESCRUB_DATASET_ZIP_DRIVE_ID $WORKDIR
#RUN tar xzf $FACESCRUB_DATASET_ZIP_DRIVE_ID -C $WORKDIR
#COPY /tmp/facescrub_dataset.tar.gz $WORKDIR

### This is a debug/dev dataset, it can be removed once the IMG_BASE_DIR is in S3
#ENV SEED_IMAGES_ZIP_DRIVE_ID 0Bzt4aP7vYnOTamRXQWpPT25WSVk
#RUN wget --no-check-certificate https://googledrive.com/host/$SEED_IMAGES_ZIP_DRIVE_ID -O /tmp/seed_images.zip && \
#    tar xvf /tmp/seed_images.zip -C $IMG_BASE_DIR && \
#    rm /tmp/seed_images.zip
# ADD https://googledrive.com/host/$SEED_IMAGES_ZIP_DRIVE_ID $IMG_BASE_DIR/seed_images.tar.gz

CMD /usr/local/bin/gunicorn web.wsgi:application -w 2 -b :8000 --reload
