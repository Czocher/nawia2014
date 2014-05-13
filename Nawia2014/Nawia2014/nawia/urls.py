from django.conf.urls import patterns, url

urlpatterns = patterns('',
    (r'^$', 'nawia.views.home'),
    (r'^home$', 'nawia.views.home'),
    (r'^help$', 'nawia.views.help'),
    (r'^account$', 'nawia.views.account'),
)