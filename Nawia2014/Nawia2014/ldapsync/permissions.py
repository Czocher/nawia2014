# -*- coding: utf-8 -*-

u'''
Moduł zapewniający funkcje służące do rejestracji użytkowników w systemie przydzielania uprawnień.

Moduł jest wykorzystywany w module synchronizującym lokalne modele z systemem LDAP.

Przed rejestrowaniem użytkowników należy wywołać funkcję 'prepareForSync()',
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
    createPermissions()
    createGroups()

def clear():
    clearPermissions()
    clearGroups()

def reload():
    clear()
    initialize()

def prepareForSync():
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
    Usuwa z bazy obiekty uprawnień definiowane przez moduł.
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
    Usuwa z bazy obiekty grup definiowane przez moduł.
    ''' 
    for key, value in __groups.iteritems():
        try:
            group = __group(key)
            group.delete()
            print u"Group '{}' has been deleted.".format(group)
        except DoesNotExist:
            pass

def registerDepartmentHead(employee):
    employee.user.groups.add(__group(DEPARTMENT_HEAD_GROUP))

def registerFacultyHead(employee):
    employee.user.groups.add(__group(FACULTY_HEAD_GROUP))

def registerStudent(student):
    student.user.groups.add(__group(STUDENTS_GROUP))

def registerEmployee(employee):
    if employee.isDoctorOrAbove:
        registerDoctor(employee)

def registerOrganization(organization):
    registerThesisTopicAuthor(organization.user)

def registerDoctor(employee):
    u'''
    Skrót pozwalający nadać użytkownikowi prawa do tworzenia tematów prac, bycia promotorem oraz recenzentem.
    '''
    registerThesisTopicAuthor(employee.user)
    registerSupervisor(employee)
    registerReviewer(employee)

def registerThesisTopicAuthor(user):
    u'''
    Oczekiwany typ parametru to User, ponieważ autor tematów prac może być pracownikiem (Employee) lub podmiotem zewnętrznym (Organization).
    '''
    user.groups.add(__group(THESIS_SUBJECT_AUTHORS_GROUP))

def registerReviewer(employee):
    employee.user.groups.add(__group(REVIEWERS_GROUP))

def registerSupervisor(employee):
    employee.user.groups.add(__group(SUPERVISORS_GROUP))

def __permission(key):
    try:
        contentType = ContentType.objects.get_for_model(key[0])
        permission = Permission.objects.filter(codename = key[1], content_type = contentType)
        if permission:
            return permission[0]
        else:
            raise DoesNotExist 
    except OperationalError:
        return None

# Słownik uprawnień, gdzie kluczem jest (obiekt kontekstu, nazwa kodowa), a wartością nazwa opisowa.
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

# Słownik uprawnień, gdzie kluczem jest nazwa kodowa grupy, a wartością krotka (nazwa grupy, lista uprawnień).
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