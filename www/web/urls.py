from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from django.contrib import admin

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'},  name='logout'),
    url(r'', include('face_matcher.urls', namespace='face_matcher')),
)

if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'^media/(?P<path>.*)',
        'serve',
        {'document_root': settings.MEDIA_ROOT}),
)
