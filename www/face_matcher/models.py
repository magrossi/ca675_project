import os, os.path
from django.db import models
from django.conf import settings

class Actor(models.Model):
    MALE = 'M'
    FEMALE = 'F'
    GENDER_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )

    name = models.CharField(max_length=100, blank=False)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=MALE, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', 'gender',)


class Face(models.Model):
    ACTOR_SOURCE = 'A'
    USER_SOURCE = 'U'

    url = models.URLField(max_length=2000, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    actor = models.ForeignKey('Actor', on_delete=models.CASCADE, null=True)
    face_bbox = models.CharField(max_length=100, blank=False)
    face_img_path = models.CharField(max_length=2000, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def face_source(self):
        return self.ACTOR_SOURCE if self.actor is not None else self.USER_SOURCE

    @property
    def bbox(self):
        return map(lambda s: int(s), self.face_bbox.split(','))

    def __unicode__(self):
        return self.url

    class Meta:
        ordering = ('created_at',)

class History(models.Model):
    PENDING = 'P'
    RUNNING = 'R'
    FINISHED = 'F'
    ERROR = 'E'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (FINISHED, 'Finished'),
        (ERROR, 'Error'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    run_params = models.CharField(max_length=2000, null=True)
    status = models.CharField(max_length=1,blank=False,choices=STATUS_CHOICES, default=PENDING)
    in_face = models.ForeignKey('Face', on_delete=models.CASCADE)
    output = models.TextField(null=True)
    finished_at = models.DateTimeField(null=True)

    class Meta:
        ordering = ('created_at',)

class HistoryItem(models.Model):
    history = models.ForeignKey('History', on_delete=models.CASCADE)
    face = models.ForeignKey('Face', on_delete=models.CASCADE)
    similarity_score = models.FloatField(null=False)

    class Meta:
        ordering = ('history','similarity_score',)
