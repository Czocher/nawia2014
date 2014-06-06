from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template import RequestContext, loader
from django.views.generic import ListView
from topics.models import ThesisTopic, ThesisTopicStateChange
from authorships.models import Authorship

u"""
widoki modulu studenta
"""

# widok strony glownej
def home(request):
    template = loader.get_template('student/home.html')
    context = RequestContext(request, {
    })
    return HttpResponse(template.render(context))

def list(request):
    topic_list = ThesisTopic.objects.all()
    template = loader.get_template('student/list.html')
    context = RequestContext(request, {
        'topic_list' : topic_list,
        'list_title' : ThesisTopic._meta.verbose_name_plural,
        'title' : ThesisTopic._meta.get_field_by_name('title')[0].verbose_name,
        'author' : ThesisTopic._meta.get_field_by_name('author')[0].verbose_name,
        'keywords' : ThesisTopic._meta.get_field_by_name('keywords')[0].verbose_name,
        'coworkersLimit' : ThesisTopic._meta.get_field_by_name('coworkersLimit')[0].verbose_name,
    })
    return HttpResponse(template.render(context))

def preview_list(request, subject_id):
    #int_id = int(subject_id)
    try:
        thesis_subject = ThesisTopic.objects.get(id=subject_id)
    except ThesisTopic.DoesNotExist:
        raise Http404
    context = RequestContext(request, {
        'subject' : thesis_subject,
    })
    return HttpResponse(template.render(context))

def preview_list(request, filter):
    thesis_subject = ThesisTopic.objects.filter(field_type=field_value)
    context = RequestContext(request, {
        'subject' : thesis_subject,
    })
    return HttpResponse(template.render(context))

#TODO: models.py - add observed list
def observed(request):
    template = loader.get_template('student/observed.html')
    context = RequestContext(request, {
    })
    return HttpResponse(template.render(context))

def applied(request):
    template = loader.get_template('student/applied.html')
    context = RequestContext(request, {
    })
    return HttpResponse(template.render(context))

def assigned(request):
    template = loader.get_template('student/assigned.html')
    context = RequestContext(request, {
    })
    return HttpResponse(template.render(context))

# strona pomocy modulu studenta
def help(request):
    return render(request, 'stHelp.html', {})

# wylaczne ustawienia konta dla modulu studenta
def account(request):
    return render(request, 'stAccount.html', {})

# widok listy tematow
class List(ListView):
    model = ThesisTopic
    context_object_name = 'thesisTopics'
    template_name = 'student/list.html'

# widok przefiltrowanej listy tematow
class ListFiltered(ListView):
    model = ThesisTopic
    context_object_name = 'thesisTopics'
    template_name = 'student/list.html'

    def get_queryset(self):
        #wyciagniecie filtru z urlu
        filter_string = self.args[0]
        # logika oddzielajaca w stringu pola typu typ, promotor, tytul
        
        # filtrowanie pracy - praca jest opublikowana (mozna sie na nia zglaszac)
        
        list = ThesisTopic.objects.filter(state__state = ThesisTopicStateChange.PUBLISHED)   

        # filtrowanie pracy - po tytule
        #list = list.filter(title__contains="test")  
        
        ## filtrowanie pracy - po opisie   
        #list = list.filter(description__contains="test")

        ## filtrowanie pracy - po limicie osob ja piszacych
        #list = list.filter(coworkersLimit__lte="1")

        return list 
    
# dodanie tematu pracy do Obserwowanych
def addToObserved_list(request, id):
    return List.as_view()(request)

# dodanie tematu pracy do Kolejki wybranych prac
def addToQueue_list(request, id):
    return List.as_view()(request)

# widok kontaktu z promotorem
def contact(request, id):
    return List.as_view()(request)

# widok listy Obserwowanych
class Observed(ListView):
    model = ThesisTopic
    context_object_name = 'observedList'
    template_name = 'stObserved.html'

    def get_queryset(self):
        observed = Authorship.objects.all().filter(student=1).filter(state='p')
        return observed 

# widok przefiltrowanej listy Obserwowanych
class ObservedFiltered(ListView):
    model = ThesisTopic
    context_object_name = 'observedList'
    template_name = 'stObserved.html'

    def get_queryset(self):
        # logika oddzielajaca w stringu pola typu typ, promotor, tytul
        
        # zamiast zwracania wszystkich obiektow, filtrowanie wynikow
        return ThesisTopic.objects.all() 

