from django.db import models
from django.conf import settings


class Upload(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(max_length=2000, blank=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.url

    class Meta:
        ordering = ('created_at',)
