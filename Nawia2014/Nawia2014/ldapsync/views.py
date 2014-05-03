from django.http.response import HttpResponse
from ldapsync import LdapSync

def sync(request):
    LdapSync.sync()
    return HttpResponse("Synchronization with LDAP has been completed.")