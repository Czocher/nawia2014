from django.conf.urls import patterns, url
from student.views import List
from student.views import ListFiltered
from student.views import Observed

urlpatterns = patterns('student.views',
    (r'^$', 'home'),
    (r'^home$', 'home'),

    (r'^list$', 'list'),
    (r'^list/preview/(?P<subject_id>[0-9]+)$', 'preview_list'),

    (r'^observed$', 'observed'),
    (r'^applied$', 'applied'),
    (r'^assigned$', 'assigned'),
    (r'^help$', 'help'),
    (r'^account$', 'account'),

    #pozostawione, do weryfikacji
    (r'^list/([\w-]+)/$', ListFiltered.as_view()),
    
    (r'^list/addToObserved/(?P<id>[0-9]+)$', 'addToObserved_list'),
    (r'^list/addToQueue/(?P<id>[0-9]+)$', 'addToQueue_list'),

    (r'^supervisor/contact/(?P<id>[0-9]+)$', List.as_view()),

    (r'^observed/$', Observed.as_view()),
    (r'^observed/([\w-]+)/$', Observed.as_view()),
    (r'^observed/preview/(?P<id>[0-9]+)$', List.as_view()),
    (r'^observed/remove/(?P<id>[0-9]+)$', List.as_view()),
    (r'^observed/addToQueue/(?P<id>[0-9]+)$', List.as_view()),

    (r'^applied/$', List.as_view()),
    (r'^applied/([\w-]+)/$', List.as_view()),
    (r'^applied/preview/(?P<id>[0-9]+)$', List.as_view()),
    (r'^applied/remove/(?P<id>[0-9]+)$', List.as_view()),

    (r'^asigned/$', List.as_view()),
    (r'^asigned/([\w-]+)/$', List.as_view()),
    (r'^asigned/preview/(?P<id>[0-9]+)$', List.as_view()),
    (r'^asigned/schedule/(?P<id>[0-9]+)$', List.as_view()),
    (r'^asigned/abandon/(?P<id>[0-9]+)$', List.as_view()),
    (r'^asigned/sendFiles/(?P<id>[0-9]+)$', List.as_view()),
    (r'^asigned/contact/(?P<id>[0-9]+)$', List.as_view()),
)