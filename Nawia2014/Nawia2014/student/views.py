from django.http import HttpResponse
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

#TODO: pobrac liste tematow, umiescic ja w kontekscie
def list(request):
    template = loader.get_template('student/list.html')
    context = RequestContext(request, {
    })
    return HttpResponse(template.render(context))

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

# podglad tematu pracy
def preview_list(request, subject_id):
    int_id = int(subject_id)
    try:
        thesis_subject = ThesisSubject.objects.all().get(id=int_id)
    except ThesisSubject.DoesNotExist:
        return render(request, 'error.html', {})
    
    return render(request, 'stPreview.html', {'thesisSubject':thesis_subject})
    
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

