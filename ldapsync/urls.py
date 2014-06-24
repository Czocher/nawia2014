from django.conf.urls import patterns, url

urlpatterns = patterns('ldapsync.views',
    url(r'^$', 'sync', name='sync'),
)
