from django.db import models
from django.conf import settings

class Face(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(max_length=2000, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    actor = models.ForeignKey('Actor', on_delete=models.CASCADE)
    bbox = models.CharField(max_length=100, blank=False)
    source_type = models.CharField(max_length=1, choices=(('U', 'User'), ('A', 'Actor'),), blank=False, default='U')
    face_img = models.ImageField(blank=False)

    def __unicode__(self):
        return self.url

    class Meta:
        ordering = ('created_at',)

class Actor(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=False)
    gender = models.CharField(max_length=1, choices=(('F', 'Female'),('M', 'Male'),), blank=False)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name', 'gender',)

class Upload(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(max_length=2000, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.url

    class Meta:
        ordering = ('created_at',)
