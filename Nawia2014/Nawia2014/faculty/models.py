# -*- coding: utf-8 -*-

u'''
Aplikacja 'faculty' zapewnia szereg modeli odwzorowujących strukturę wydziału.
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
    '''

    class Meta:
        verbose_name = _('StudyCycle')
        verbose_name_plural = _('StudyCycles')

    ldapId = models.CharField(editable = False, max_length = 255, unique = True)

    name = models.CharField(max_length = 255,
                            verbose_name = _('StudyCycle/name'))

    submissionsOpenAt = models.DateField(default = None, null = True, blank = True,
                                         verbose_name = _('StudyCycle/start of submissions'))
    submissionsCloseAt = models.DateField(default = None, null = True, blank = True,
                                          verbose_name = _('StudyCycle/end of submissions'))

    isLdapSynced = models.BooleanField(default = False,
                                       verbose_name = _('LDAP synced'))

    # relacje odwrotne
    # self.students : List<Student>
    # self.thesisTopics : List<ThesisTopic>
        
    def __unicode__(self):
        return self.name

class UserBasedModel(models.Model):
    u'''
    Abstrakcyjny model zapewniający powiązanie obiektów studenta, pracownika, organizacji zewnętrznej z obiektami django.contrib.auth.models.User.
    '''

    class Meta:
        abstract = True
        ordering = ('user', )

    user = models.OneToOneField(User, verbose_name = _('UserBasedModel/user'))
    isLdapSynced = models.BooleanField(default=False, editable=False,
                                       verbose_name = _('LDAP synced'))


class Student(UserBasedModel):
    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('Students')

    # jeden student może realizować wiele cykli kształcenia
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
    Pracownik uczelni.
    '''

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')

    # tytuł naukowy
    title = models.CharField(max_length = 255, blank = True,
                             verbose_name = _('Employee/academic title'))
    # stanowisko pracy (asystent, adiunkt, itp.)
    position = models.CharField(max_length = 255, blank = True,
                                verbose_name = _('Employee/position'))
    # jednostka organizacyjna (katedra, zakład, itp.), do której należy dany pracownik
    organizationalUnit = models.ForeignKey('OrganizationalUnit', null = True, blank = True,
                                           related_name = 'employees',
                                           verbose_name = _('Employee/organizational unit'))

    # self.isDoctorOrAbove : bool
    # self.canSupervise : bool
    # self.canReview : bool

    def __getattr__(self, name):
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
    Organizacja zewnętrzna (firma, stowarzyszenie, urząd, itp.).
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
    '''

    class Meta:
        verbose_name = _('OrganizationalUnit')
        verbose_name_plural = _('OrganizationalUnits')
        ordering = ('name', )

    ldapId = models.CharField(max_length = 31, unique = True)

    name = models.CharField(max_length = 255, verbose_name = _('OrganizationalUnit/name'))
    head = models.ForeignKey(Employee, null = True, blank = True, verbose_name = _('OrganizationalUnit/head'))

    # relacja odwrotna
    # self.employees : List<Employees>

    def __unicode__(self):
        return self.name

class Authority(models.Model):
    u'''
    Władze wydziału.
    '''
        
    class Meta:
        verbose_name = _('Authority')
        verbose_name_plural = _('Authorities')
        ordering = ('role', )

    DEAN = 'd'
    VICE_DEAN_FOR_PROMOTION = 'pr'
    VICE_DEAN_FOR_RESEARCH = 'sc'
    VICE_DEAN_FOR_STUDENTS = 'st'
    AUTHORITY_ROLES_CHOICES = (
        (DEAN, _('Dean')),
        (VICE_DEAN_FOR_PROMOTION, _('Vice-Dean for Promotion and Cooperation')),
        (VICE_DEAN_FOR_RESEARCH, _('Vice-Dean for Research')),
        (VICE_DEAN_FOR_STUDENTS, _('Vice-Dean for Teaching and Students')),
    )
    role = models.CharField(max_length = 2,
                            choices = AUTHORITY_ROLES_CHOICES,
                            verbose_name = _('Authority/role'))
    occupant = models.ForeignKey(Employee, null = True, blank = True,
                                 verbose_name = _('Authority/occupant'))

    def __unicode__(self):
        return u'%s (%s)' % (self.occupant, self.get_role_display())