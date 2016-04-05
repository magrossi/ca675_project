# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings

from face_matcher.models import Face, Actor

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, blank=False)),
                ('gender', models.CharField(default=b'M', max_length=1, choices=((b'M', b'Male'),(b'F', b'Female'),), blank=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('name', 'gender',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Face',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.URLField(max_length=2000, blank=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
                ('actor', models.ForeignKey(to='face_matcher.Actor', null=True)),
                ('face_bbox', models.CharField(max_length=100, blank=False)),
                ('face_img_path', models.CharField(max_length=2000, blank=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('created_at',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('run_params', models.CharField(max_length=2000, null=True)),
                ('status', models.CharField(default=b'P', max_length=1, choices=[(b'P', b'Pending'), (b'R', b'Running'), (b'F', b'Finished'), (b'E', b'Error')])),
                ('output', models.TextField(null=True)),
                ('finished_at', models.DateTimeField(null=True)),
                ('in_face', models.ForeignKey(to='face_matcher.Face')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created_at',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='HistoryItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('similarity_score', models.FloatField()),
                ('face', models.ForeignKey(to='face_matcher.Face')),
                ('history', models.ForeignKey(to='face_matcher.History')),
            ],
            options={
                'ordering': ('history', 'similarity_score'),
            },
            bases=(models.Model,),
        ),
    ]
