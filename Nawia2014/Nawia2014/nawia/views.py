from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render

# strona glowna aplikacji
def home(request):
    return render(request, 'home.html', {})

# strona pomocy
def help(request):
    return render(request, 'help.html', {})

# strona ustawien konta
def account(request):
    return render(request, 'account.html', {})
