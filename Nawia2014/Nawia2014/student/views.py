from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import redirect
from django.shortcuts import render
from django.template import RequestContext, loader
from django.views.generic import ListView
from nawia.models import ThesisSubject
from nawia.models import Authorship
from nawia.models import ThesisSubjectStateChange

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
    topic_list = ThesisSubject.objects.all()
    template = loader.get_template('student/list.html')
    context = RequestContext(request, {
        'topic_list' : topic_list,
        'list_title' : ThesisSubject._meta.verbose_name_plural,
        'title' : ThesisSubject._meta.get_field_by_name('title')[0].verbose_name,
        'author' : ThesisSubject._meta.get_field_by_name('author')[0].verbose_name,
        'keywords' : ThesisSubject._meta.get_field_by_name('keywords')[0].verbose_name,
        'teamMembersLimit' : ThesisSubject._meta.get_field_by_name('teamMembersLimit')[0].verbose_name,
    })
    return HttpResponse(template.render(context))

def preview_list(request, subject_id):
    #int_id = int(subject_id)
    try:
        thesis_subject = ThesisSubject.objects.get(id=subject_id)
    except ThesisSubject.DoesNotExist:
        raise Http404
    context = RequestContext(request, {
        'subject' : thesis_subject,
    })
    return HttpResponse(template.render(context))

def preview_list(request, filter):
    thesis_subject = ThesisSubject.objects.filter(field_type=field_value)
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
    model = ThesisSubject
    context_object_name = 'thesisSubjects'
    template_name = 'stList.html'

# widok przefiltrowanej listy tematow
class ListFiltered(ListView):
    model = ThesisSubject
    context_object_name = 'thesisSubjects'
    template_name = 'stList.html'

    def get_queryset(self):
        #wyciagniecie filtru z urlu
        filter_string = self.args[0]
        # logika oddzielajaca w stringu pola typu typ, promotor, tytul
        
        # filtrowanie pracy - praca jest opublikowana (mozna sie na nia zglaszac)
        
        list = ThesisSubject.objects.all().filter(state=ThesisSubjectStateChange.PUBLISHED)   

        # filtrowanie pracy - po tytule
        list = list.filter(title__contains="test")  
        
        # filtrowanie pracy - po opisie   
        list = list.filter(description__contains="test")

        # filtrowanie pracy - po limicie osob ja piszacych
        list = list.filter(teamMembersLimit__lte="1")

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
    model = ThesisSubject
    context_object_name = 'observedList'
    template_name = 'stObserved.html'

    def get_queryset(self):
        observed = Authorship.objects.all().filter(student=1).filter(state='p')
        return observed 

# widok przefiltrowanej listy Obserwowanych
class ObservedFiltered(ListView):
    model = ThesisSubject
    context_object_name = 'observedList'
    template_name = 'stObserved.html'

    def get_queryset(self):
        # logika oddzielajaca w stringu pola typu typ, promotor, tytul
        
        # zamiast zwracania wszystkich obiektow, filtrowanie wynikow
        return ThesisSubject.objects.all() 

