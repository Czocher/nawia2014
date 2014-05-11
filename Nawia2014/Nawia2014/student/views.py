from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import ListView
from nawia.models import ThesisSubject

class List(ListView):
    model = ThesisSubject
    context_object_name = 'thesisSubjects'
    template_name = 'stList.html'

class ListFiltered(ListView):
    model = ThesisSubject
    context_object_name = 'thesisSubjects'
    template_name = 'stList.html'

    def get_queryset(self):
        # logika oddzielajaca w stringu pola typu typ, promotor, tytul
        
        # zamiast zwracania wszystkich obiektow, filtrowanie wynikow
        return ThesisSubject.objects.all() 

def home(request):
    return render(request, 'stIndex.html', {})

def help(request):
    return render(request, 'stHelp.html', {})

def account(request):
    return render(request, 'stAccount.html', {})
    
def addToObserved(request, thesis_id):
    return List.as_view()(request)


