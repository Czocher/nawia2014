from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template import RequestContext, loader

# strona glowna aplikacji
def home(request):
    template = loader.get_template('nawia/home.html')
    context = RequestContext(request, {
    })
    return HttpResponse(template.render(context))


# strona pomocy
def help(request):
    template = loader.get_template('nawia/help.html')
    context = RequestContext(request, {
    })
    return HttpResponse(template.render(context))

# strona ustawien konta
def account(request):
    template = loader.get_template('nawia/account.html')
    context = RequestContext(request, {
    })
    return HttpResponse(template.render(context))
