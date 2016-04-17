#!/usr/bin/env python
import urllib
from os.path import expandvars

MODELFILE_URL = 'http://www.googledrive.com/host/0Bzt4aP7vYnOTYXpodUFmMlY4WVU/model.dat'
DATASETFILE_URL = 'http://www.googledrive.com/host/0Bzt4aP7vYnOTYXpodUFmMlY4WVU/dataset.dat'


# Fetch pre-calculated datafiles
urllib.urlretrieve(MODELFILE_URL, filename=expandvars("$WORKDIR/model.dat"))
urllib.urlretrieve(DATASETFILE_URL, filename=expandvars("$WORKDIR/dataset.dat"))
