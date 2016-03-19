import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web.settings')
django.setup()

from django_seed import Seed
from django.contrib.auth.models import User
from face_matcher.models import Upload


seeder = Seed.seeder()

seeder.add_entity(User, 5)
seeder.add_entity(Upload, 10, {
    'url': lambda x: 'http://lorempixel.com/400/200/',
})

inserted_pks = seeder.execute()
