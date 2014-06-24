# -*- coding: utf-8 -*-

u''' @package ldapsync.permissions
Moduł zapewniający funkcje służące do rejestracji użytkowników w systemie przydzielania uprawnień.

Moduł jest wykorzystywany w module synchronizującym lokalne modele z systemem LDAP.

Przed rejestrowaniem użytkowników należy wywołać funkcję prepareForSync(),
która usunie i stworzy na nowo niezbędne obiekty uprawnień oraz grup,
jednocześnie zrywając wcześniejsze powiązania użytkowników z uprawnieniami.
'''

from django.utils.translation import pgettext
from django.contrib.auth.models import Permission, Group
from django.db.utils import OperationalError
from django.contrib.contenttypes.models import ContentType
from topics.models import ThesisTopic
from authorships.models import SubmissionCriterion, Authorship, SubmissionCriterionValue
from reviews.models import Review
from theses.models import Thesis

def initialize():
    u'''
    Tworzy (jeśli nie istnieją) obiekty używanych przez moduł uprawnień i ich grup.
    '''
    createPermissions()
    createGroups()

def clear():
    u'''
    Usuwa (jeśli istnieją) z bazy obiekty używanych przez moduł uprawnień i ich grup.
    '''
    clearPermissions()
    clearGroups()

def reload():
    u'''
    Usuwa i tworzy od nowa używanych przez moduł uprawnień i ich grup.
    Tym samym w łatwy sposób zrywa powiązania pomiędzy użytkownikami a uprawnieniami i grupami.
    '''
    clear()
    initialize()

def prepareForSync():
    u'''
    Alias do funkcji reload().
    '''
    reload()

def createPermissions():
    u'''
    Dodaje do bazy niezbędne obiekty uprawnień wykorzystywane przez moduł.
    ''' 
    for key, value in __permissions.iteritems():
        try:
            permission = __permission(key)
        except DoesNotExist:
            # Jeśli dane uprawnienie nie istnieje w bazie, należy je utworzyć.
            contentType = ContentType.objects.get_for_model(key[0])
            newPermission = Permission.objects.create(codename = key[1],
                                                      name = value,
                                                      content_type = contentType)
            print u"Permission '{}' has been created.".format(newPermission)

def clearPermissions():
    u'''
    Usuwa z bazy obiekty uprawnień wykorzystywane przez moduł.
    ''' 
    for key, value in __permissions.iteritems():
        try:
            permission = __permission(key)
            permission.delete()
            print u"Permission '{}' has been deleted.".format(permission)
        except DoesNotExist:
            pass

def createGroups():
    u'''
    Dodaje do bazy niezbędne obiekty grup wykorzystywane przez moduł.
    ''' 
    for key, value in __groups.iteritems():
        try:
            group = __group(key)
        except DoesNotExist:
            # Jeśli dana grupa nie istnieje w bazie, należy ją utworzyć.
            newGroup = Group.objects.create(name = value[0])
            newGroup.save()
            for permission in value[1]:
                p = __permission(permission)
                newGroup.permissions.add(p)
            print u"Group '{}' has been created.".format(newGroup)

def clearGroups():
    u'''
    Usuwa z bazy obiekty grup wykorzystywane przez moduł.
    ''' 
    for key, value in __groups.iteritems():
        try:
            group = __group(key)
            group.delete()
            print u"Group '{}' has been deleted.".format(group)
        except DoesNotExist:
            pass

def registerStudent(student):
    u'''
    Rejestruje studenta, przydzielając go do odpowiedniej grupy.

    @param student faculty.models.Student student
    '''
    student.user.groups.add(__group(STUDENTS_GROUP))

def registerEmployee(employee):
    u'''
    Rejestruje pracownika, przydzielając go do odpowiednich grup.

    @param employee faculty.models.Employee pracownik
    '''
    if employee.isDoctorOrAbove:
        registerDoctor(employee)

def registerOrganization(organization):
    u'''
    Rejestruje organizację zewnętrzną, przydzielając jej przedstawiciela do odpowiednich grup.

    @param organization faculty.models.Organization organizacja zewnętrzna
    '''
    registerThesisTopicAuthor(organization.user)


def registerDepartmentHead(employee):
    u'''
    Rejestruje pracownika jako kierownika katedry, przydzielając go do odpowiedniej grupy.

    @param employee faculty.models.Employee pracownik mający pełnić rolę kierownika katedry
    '''
    employee.user.groups.add(__group(DEPARTMENT_HEAD_GROUP))

def registerFacultyHead(employee):
    u'''
    Rejestruje pracownika jako dziekana, przydzielając go do odpowiedniej grupy.

    @param employee faculty.models.Employee pracownik mający pełnić rolę dziekana
    '''
    employee.user.groups.add(__group(FACULTY_HEAD_GROUP))

def registerDoctor(employee):
    u'''
    Skrót pozwalający nadać użytkownikowi prawa do tworzenia tematów prac, bycia promotorem oraz recenzentem.

    @param employee faculty.models.Employee pracownik mający tytuł naukowy doktora (co najmniej)
    '''
    registerThesisTopicAuthor(employee.user)
    registerSupervisor(employee)
    registerReviewer(employee)

def registerThesisTopicAuthor(user):
    u'''
    Rejestruje użytkownika jako twórcę tematów pracy.
    Oczekiwany typ parametru to User, ponieważ autor tematów prac może być pracownikiem
    (faculty.models.Employee) lub podmiotem zewnętrznym (faculty.models.Organization).
    
    @param user User użytkownik mogący proponować tematy prac
    '''
    user.groups.add(__group(THESIS_SUBJECT_AUTHORS_GROUP))

def registerReviewer(employee):
    u'''
    Rejestruje pracownika jako potencjalnego recenzenta.
    
    @param employee faculty.models.Employee pracownik mogący być recenzentem
    '''
    employee.user.groups.add(__group(REVIEWERS_GROUP))

def registerSupervisor(employee):
    u'''
    Rejestruje pracownika jako potencjalnego promotora.
    
    @param employee faculty.models.Employee pracownik mogący być promotorem
    '''
    employee.user.groups.add(__group(SUPERVISORS_GROUP))

def __permission(key):
    u'''
    Getter obiektu uprawnienia.
    
    @param key tuple (obiekt kontekstu, nazwa kodowa)
    @returns Permission
    '''
    try:
        contentType = ContentType.objects.get_for_model(key[0])
        permission = Permission.objects.filter(codename = key[1], content_type = contentType)
        if permission:
            return permission[0]
        else:
            raise DoesNotExist 
    except OperationalError:
        return None

## Słownik uprawnień, gdzie kluczem jest krotka (obiekt kontekstu, nazwa kodowa), a wartością nazwa opisowa.
## Niestety wygląda to bardzo nieelegancko, ponieważ 'pgettext' nie występuje w postaci skrótowej
#  (tzn. może w niej występować, ale wtedy byłaby konieczność napisania własnego parsera na kształt 'makemessages').
## Niestety nie możemy także wpisać zmiennej albo stałej jako któregokolwiek z parametrów 'pgettext'
#  (znowu ułomność 'makemessages').
__permissions = {
    (ThesisTopic, 'canCreate'): pgettext('permission description', 'can create thesis subject'),
    (ThesisTopic, 'canModify'): pgettext('permission description', 'can modify thesis subject'),
    (ThesisTopic, 'canCancel'): pgettext('permission description', 'can cancel thesis subject'),
    (ThesisTopic, 'canPublish'): pgettext('permission description', 'can publish thesis subject'),
    (ThesisTopic, 'canAccept'): pgettext('permission description', 'can accept thesis subject'),
    (ThesisTopic, 'canReject'): pgettext('permission description', 'can reject thesis subject'),
    (SubmissionCriterion, 'canDefine'): pgettext('permission description', 'can define criterion of submission for thesis subject'),
    (SubmissionCriterionValue, 'canFill'): pgettext('permission description', 'can fill value of criterion of submission for thesis subject'),
    (Authorship, 'canAccept'): pgettext('permission description', 'can accept submission for thesis subject'),
    (Authorship, 'canReject'): pgettext('permission description', 'can reject submission for thesis subject'),
    (Authorship, 'canPropose'): pgettext('permission description', 'can propose submission for thesis subject'),
    (Authorship, 'canCancel'): pgettext('permission description', 'can cancel submission for thesis subject'),
    (Review, 'canPropose'): pgettext('permission description', 'can propose reviewer'),
    (Review, 'canAssign'): pgettext('permission description', 'can assign reviewer'),
    (Review, 'canWrite'): pgettext('permission description', 'can write review'),
    (Thesis, 'canAccept'): pgettext('permission description', 'can accept thesis'),
    (Thesis, 'canCancel'): pgettext('permission description', 'can cancel thesis'),
}

def __group(key):
    u'''
    Getter obiektu grupy.
    
    @param key string nazwa grupy
    @returns Group
    '''
    try:
        x = unicode(__groups[key][0])
        group = Group.objects.filter(name = x)
        if group:
            return group[0]
        else:
            raise DoesNotExist 
    except OperationalError:
        return None
    
STUDENTS_GROUP = 'students'
SUPERVISORS_GROUP = 'supervisors'
REVIEWERS_GROUP = 'reviewers'
THESIS_SUBJECT_AUTHORS_GROUP = 'thesis subject authors'
FACULTY_HEAD_GROUP = 'heads of faculty'
DEPARTMENT_HEAD_GROUP = 'heads of departments'

## Słownik uprawnień, gdzie kluczem jest nazwa kodowa grupy, a wartością krotka (nazwa grupy, lista uprawnień).
__groups = {
    STUDENTS_GROUP: (pgettext('group name', 'students'), [
                        (SubmissionCriterionValue, 'canFill'),
                        (Authorship, 'canPropose'),
                        (Authorship, 'canCancel'),
                    ]),
    SUPERVISORS_GROUP: (pgettext('group name', 'supervisors'), [
                            (Review, 'canPropose'),
                            (Thesis, 'canAccept'),
                            (Thesis, 'canCancel'),
                       ]),
    REVIEWERS_GROUP: (pgettext('group name', 'reviewers'), [
                        (Review, 'canWrite'),
                     ]),
    THESIS_SUBJECT_AUTHORS_GROUP: (pgettext('group name', 'thesis subject authors'), [
                                        (ThesisTopic, 'canCreate'),
                                        (ThesisTopic, 'canModify'),
                                        (ThesisTopic, 'canCancel'),
                                        (ThesisTopic, 'canPublish'),
                                        (SubmissionCriterion, 'canDefine'),
                                        (Authorship, 'canAccept'),
                                        (Authorship, 'canReject'),
                                  ]),
    FACULTY_HEAD_GROUP: (pgettext('group name', 'heads of faculty'), [
                            (ThesisTopic, 'canAccept'),
                            (ThesisTopic, 'canReject'),
                            (Review, 'canAssign'),
                        ]),
    DEPARTMENT_HEAD_GROUP: (pgettext('group name', 'heads of departments'), [
                                (ThesisTopic, 'canAccept'),
                                (ThesisTopic, 'canReject'),
                                (Review, 'canAssign'),
                           ]),
}

class DoesNotExist(Exception):
    def __init__(self, value = 'Permission'):
        self.value = value
    
    def __str__(self):
        return "%s does not exist." % (self.value)