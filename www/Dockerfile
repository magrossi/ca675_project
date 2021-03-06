FROM buildpack-deps:jessie

### Linux deps
RUN set -ex \
  && apt-get update \
  && apt-get install -y postgresql-client libblas-dev liblapack-dev libatlas-base-dev gfortran unzip \
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
## Directories
ENV WORKDIR /usr/src/app
RUN mkdir -p $WORKDIR/static
WORKDIR $WORKDIR

## Requirements
COPY requirements.txt $WORKDIR
RUN pip install --no-cache-dir -r requirements.txt

## Fetch large assets
ENV FACESCRUB_DATASET_DRIVE_ID 0BwskLTzFnnxpbHoxUmhham9mUzQ
RUN wget --no-check-certificate https://googledrive.com/host/$FACESCRUB_DATASET_DRIVE_ID -O $WORKDIR/facescrub_dataset.txt
ENV PREGENERATED_BMPS_DRIVE_ID 0BwskLTzFnnxpM3A4Rk9uZEtKXzQ
RUN wget --no-check-certificate https://googledrive.com/host/$PREGENERATED_BMPS_DRIVE_ID -O $WORKDIR/bmps.zip \
  && unzip $WORKDIR/bmps.zip -d $WORKDIR/static/images \
  && rm -f $WORKDIR/bmps.zip

## Volumes
VOLUME $WORKDIR/static

## Source
ADD . $WORKDIR
