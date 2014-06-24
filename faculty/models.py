# -*- coding: utf-8 -*-

u''' @package faculty.models
Moduł gromadzący modele odwzorowujące strukturę wydziału.
Modele przystosowane są do synchronizacji z systemem LDAP, zapewnianej przez moduły pochodzące z aplikacji 'ldapsync'.
'''

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class StudyCycle(models.Model):
    u'''
    Cykl kształcenia (np. informatyka, inżynierskie, stacjonarne, 2011Z-2014Z).

    Relacje odwrotne:
    StudyCycle.students : [Student]
    StudyCycle.thesisTopics : [ThesisTopic]
    '''

    class Meta:
        verbose_name = _('StudyCycle')
        verbose_name_plural = _('StudyCycles')

    ### Identyfiaktor w systemie LDAP.
    ldapId = models.CharField(editable = False, max_length = 255, unique = True)
    ### Nazwa cyklu.
    name = models.CharField(max_length = 255,
                            verbose_name = _('StudyCycle/name'))

    submissionsOpenAt = models.DateField(default = None, null = True, blank = True,
                                         verbose_name = _('StudyCycle/start of submissions'))
    submissionsCloseAt = models.DateField(default = None, null = True, blank = True,
                                          verbose_name = _('StudyCycle/end of submissions'))

    ### Określa, czy model został zsynchronizowany z bazą LDAP. Jeśli po synchronizacji ma wartość False,
    ### to odpowiedniego obiektu nie odnaleziono w bazie LDAP.
    isLdapSynced = models.BooleanField(default = False,
                                       verbose_name = _('LDAP synced'))
    
    def __unicode__(self):
        return self.name

class UserBasedModel(models.Model):
    u'''
    Abstrakcyjny model zapewniający powiązanie obiektów studenta, pracownika, organizacji zewnętrznej
    z obiektami django.contrib.auth.models.User.
    '''

    class Meta:
        abstract = True
        ordering = ('user', )

    user = models.OneToOneField(User, verbose_name = _('UserBasedModel/user'))
    ### Określa, czy model został zsynchronizowany z bazą LDAP. Jeśli po synchronizacji ma wartość False,
    ### to odpowiedniego obiektu nie odnaleziono w bazie LDAP.
    isLdapSynced = models.BooleanField(default=False, editable=False,
                                       verbose_name = _('LDAP synced'))


class Student(UserBasedModel):
    u'''
    Student (rozszerzenie modelu django.contrib.auth.models.User).
    '''
    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('Students')

    ### Cykle kształcenia przypisane do tego studenta. Jeden student może realizować wiele cykli.
    studyCycles = models.ManyToManyField(StudyCycle, null = True, blank = True,
                                         related_name = 'students',
                                         verbose_name = _('Student/study cycles'))

    #observedTopics = models.ManyToManyField(ThesisTopic, null = True, blank = True,
    #                                        related_name = 'observingStudents',
    #                                        verbose_name = _('Student/observed topics'))
    
    def __unicode__(self):
        return unicode(self.user.get_full_name())


class Employee(UserBasedModel):
    u'''
    Pracownik uczelni (rozszerzenie modelu django.contrib.auth.models.User).
    '''

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')

    ### Tytuł naukowy.
    title = models.CharField(max_length = 255, blank = True,
                             verbose_name = _('Employee/academic title'))
    ### Stanowisko pracy (asystent, adiunkt, itp.).
    position = models.CharField(max_length = 255, blank = True,
                                verbose_name = _('Employee/position'))
    ### Jednostka organizacyjna (katedra, zakład, itp.), do której należy dany pracownik.
    organizationalUnit = models.ForeignKey('OrganizationalUnit', null = True, blank = True,
                                           related_name = 'employees',
                                           verbose_name = _('Employee/organizational unit'))

    # self.isDoctorOrAbove : bool
    # self.canSupervise : bool
    # self.canReview : bool
    def __getattr__(self, name):
        u'''
        Zapewnia przekierowanie wywołań atrybutów Employee.isDoctorOrAbove, Employee.canSupervise i Employee.canReview
        na odpowiednie implementacje.
        '''
        if name == 'isDoctorOrAbove':
            return 'dr' in self.title
        elif name == 'canSupervise':
            return self.isDoctorOrAbove
        elif name == 'canReview':
            return self.isDoctorOrAbove
        else:
            raise AttributeError(name)

    def __unicode__(self):
        return '%s %s' % (self.title, self.user.get_full_name())


class Organization(UserBasedModel):
    u'''
    Organizacja zewnętrzna (firma, stowarzyszenie, urząd, itp.) - rozszerzenie modelu django.contrib.auth.models.User.
    '''

    class Meta:
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        ordering = ('name', )

    name = models.CharField(max_length = 255,
                            verbose_name = _('Organization/name'))

    def __unicode__(self):
        return '%s, %s' % (self.name, self.user.get_full_name())

class OrganizationalUnit(models.Model):
    u'''
    Jednostka organizacyjna (katedra, dziekanat, itp.).
    
    Relacje odwrotne:
    OrganizationalUnit.employees : [Employees]
    '''

    class Meta:
        verbose_name = _('OrganizationalUnit')
        verbose_name_plural = _('OrganizationalUnits')
        ordering = ('name', )

    ### Identyfiaktor w systemie LDAP.
    ldapId = models.CharField(max_length = 31, unique = True)

    name = models.CharField(max_length = 255, verbose_name = _('OrganizationalUnit/name'))
    ### Kierownik jednostki organizacyjnej.
    head = models.ForeignKey(Employee, null = True, blank = True, verbose_name = _('OrganizationalUnit/head'))

    def __unicode__(self):
        return self.name

class Authority(models.Model):
    u'''
    Przedstawiciel władz wydziału.
    '''
        
    class Meta:
        verbose_name = _('Authority')
        verbose_name_plural = _('Authorities')
        ordering = ('role', )

    ### Identyfikator roli przedstawiciela władz wydziału: Dziekan.
    DEAN = 'd'
    ### Identyfikator roli przedstawiciela władz wydziału: Prodziekan ds. Promocji i Współpracy.
    VICE_DEAN_FOR_PROMOTION = 'pr'
    ### Identyfikator roli przedstawiciela władz wydziału: Prodziekan ds. Nauki.
    VICE_DEAN_FOR_RESEARCH = 'sc'
    ### Identyfikator roli przedstawiciela władz wydziału: Prodziekan ds. Studenckich i Dydaktyki.
    VICE_DEAN_FOR_STUDENTS = 'st'
    ### Dostępne identyfikatory ról przedstawiciela władz wydziału wraz z tłumaczeniami.
    AUTHORITY_ROLES_CHOICES = (
        (DEAN, _('Dean')),
        (VICE_DEAN_FOR_PROMOTION, _('Vice-Dean for Promotion and Cooperation')),
        (VICE_DEAN_FOR_RESEARCH, _('Vice-Dean for Research')),
        (VICE_DEAN_FOR_STUDENTS, _('Vice-Dean for Teaching and Students')),
    )
    ### Rola przedstawiciela władz wydziału.
    role = models.CharField(max_length = 2,
                            choices = AUTHORITY_ROLES_CHOICES,
                            verbose_name = _('Authority/role'))
    ### Pracownik pełniący tę rolę.
    occupant = models.ForeignKey(Employee, null = True, blank = True,
                                 verbose_name = _('Authority/occupant'))

    def __unicode__(self):
        return u'%s (%s)' % (self.occupant, self.get_role_display())
