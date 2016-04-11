from django.conf.urls import patterns, url
from face_matcher import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^faces/', views.faces, name='faces'),
    url(r'^registration/', views.registration, name='registration'),
)
