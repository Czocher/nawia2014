from django.conf.urls import patterns, include, url
import ldapsync

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Nawia2014.views.home', name='home'),
    # url(r'^Nawia2014/', include('Nawia2014.Nawia2014.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^ldapsync/', include('ldapsync.urls', namespace = 'ldapsync')),
    url(r'^student/', include('student.urls', namespace = 'student')),
    url(r'^/', include('nawia.urls', namespace = 'nawia')),
)
