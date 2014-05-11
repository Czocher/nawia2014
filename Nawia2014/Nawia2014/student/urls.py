from django.conf.urls import patterns, url
from student.views import List
from student.views import ListFiltered

urlpatterns = patterns('',
    (r'^$', 'student.views.home'),
    (r'^home$', 'student.views.home'),
    (r'^help$', 'student.views.help'),
    (r'^account$', 'student.views.account'),
    (r'^list$', List.as_view()),
    (r'^list/([\w-]+)/$', ListFiltered.as_view()),
    #(r'^articles/(\d{4})/(\d{2})/$', 'news.views.month_archive'),
    #(r'^articles/(\d{4})/(\d{2})/(\d+)/$', 'news.views.article_detail'),
)