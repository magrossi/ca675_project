# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('face_matcher', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='history',
            options={'ordering': ('-created_at',)},
        ),
        migrations.AlterModelOptions(
            name='historyitem',
            options={'ordering': ('-similarity_score',)},
        ),
    ]
