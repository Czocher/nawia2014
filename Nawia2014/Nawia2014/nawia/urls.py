from django.conf.urls import patterns, url
from nawia import views

urlpatterns = patterns('',
    (r'^$', views.home),
    (r'^home$', views.home),
    (r'^help$', views.help),
    (r'^account$', views.account),
)