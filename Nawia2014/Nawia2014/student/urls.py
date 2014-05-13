from django.conf.urls import patterns, url
from student.views import List
from student.views import ListFiltered
from student.views import Observed

urlpatterns = patterns('',
    (r'^$', 'student.views.home'),
    (r'^home$', 'student.views.home'),
    (r'^help$', 'student.views.help'),
    (r'^account$', 'student.views.account'),

    (r'^list$', List.as_view()),
    (r'^list/([\w-]+)/$', ListFiltered.as_view()),
    (r'^list/preview/(?P<subject_id>[0-9]+)$', 'student.views.preview_list'),
    (r'^list/addToObserved/(?P<id>[0-9]+)$', 'student.views.addToObserved_list'),
    (r'^list/addToQueue/(?P<id>[0-9]+)$', 'student.views.addToQueue_list'),

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
    
    #(r'^articles/(\d{4})/(\d{2})/$', 'news.views.month_archive'),
    #(r'^articles/(\d{4})/(\d{2})/(\d+)/$', 'news.views.article_detail'),
)