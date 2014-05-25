# -*- coding: utf-8 -*-

u'''
Moduł zapewniający funkcje służące do rejestracji użytkowników w systemie przydzielania uprawnień.

Moduł jest wykorzystywany w module synchronizującym lokalne modele z systemem LDAP.
'''

from django.utils.translation import pgettext_lazy
from nawia.models import ThesisSubject, Authorship, Review, SubmissionCriterion, SubmissionCriterionValue, Thesis
from django.contrib.auth.models import Permission

def initialize():
    createPermissions()
    createGroups()

# Lista krotek (obiekt kontekstu, nazwa kodowa oraz nazwa opisowa) opisujących uprawnienia.
__permissions = [
    (ThesisSubject, 'canCreate', pgettext_lazy('permission description', 'can create thesis subject')),
    (ThesisSubject, 'canModify', pgettext_lazy('permission description', 'can modify thesis subject')),
    (ThesisSubject, 'canCancell', pgettext_lazy('permission description', 'can cancell thesis subject')),
    (ThesisSubject, 'canPublish', pgettext_lazy('permission description', 'can publish thesis subject')),
    (ThesisSubject, 'canAccept', pgettext_lazy('permission description', 'can accept thesis subject')),
    (ThesisSubject, 'canReject', pgettext_lazy('permission description', 'can reject thesis subject')),
    (SubmissionCriterion, 'canDefine', pgettext_lazy('permission description', 'can define criterion of submission for thesis subject')),
    (SubmissionCriterionValue, 'canFill', pgettext_lazy('permission description', 'can fill value of criterion of submission for thesis subject')),
    (Authorship, 'canAccept', pgettext_lazy('permission description', 'can accept submission for thesis subject')),
    (Authorship, 'canReject', pgettext_lazy('permission description', 'can reject submission for thesis subject')),
    (Authorship, 'canPropose', pgettext_lazy('permission description', 'can propose submission for thesis subject')),
    (Authorship, 'canCancell', pgettext_lazy('permission description', 'can cancell submission for thesis subject')),
    (Review, 'canPropose', pgettext_lazy('permission description', 'can propose reviewer')),
    (Review, 'canAssign', pgettext_lazy('permission description', 'can assign reviewer')),
    (Review, 'canWrite', pgettext_lazy('permission description', 'can write review')),
    (Thesis, 'canAccept', pgettext_lazy('permission description', 'can accept thesis')),
    (Thesis, 'canCancell', pgettext_lazy('permission description', 'can cancell thesis')),
]

def createPermissions():
    u'''
    Dodaje do bazy niezbędne obiekty uprawnień wykorzystywane przez moduł.
    '''
    from django.contrib.contenttypes.models import ContentType
    for permission in __permissions:
        contentType = ContentType.objects.get_for_model(permission[0])
        if not Permission.objects.filter(codename = permission[1], content_type = contentType):
            # Jeśli dane uprawnienie nie istnieje w bazie, należy je utworzyć.
            newPermission = Permission.objects.create(codename = permission[1],
                                      name = permission[2],
                                      content_type = contentType)
            print u"Permission '{}' has been created.".format(newPermission)

def createGroups():
    pass

def registerDepartmentHead(employee):
    pass

def registerFacultyHead(employee):
    pass

def registerStudent(student):
    pass

def registerThesisSubjectAuthor(user):
    u'''
    Oczekiwany typ parametru to User, ponieważ autor tematów prac może być pracownikiem (Employee) lub podmiotem zewnętrznym (Organization).
    '''
    pass

def registerReviewer(employee):
    pass

def registerSupervisor(employee):
    pass

def registerDoctor(employee):
    u'''
    Skrót pozwalający nadać użytkownikowi prawa do tworzenia tematów prac, bycia promotorem oraz recenzentem.
    '''
    registerThesisSubjectAuthor(employee)
    registerSupervisor(employee)
    registerReviewer(employee)

