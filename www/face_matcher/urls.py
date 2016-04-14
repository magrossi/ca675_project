from django.conf.urls import patterns, url
from face_matcher import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^matcher/', views.matcher, name='matcher'),
    url(r'^history/', views.history, name='history'),
    url(r'ajax_history/(?P<id>\d+)/$', views.ajax_get_history, name='ajax_history'),
    url(r'^registration/', views.registration, name='registration'),
)
