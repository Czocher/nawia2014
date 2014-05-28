# -*- coding: utf-8 -*-

from ldapdb.models.fields import (CharField, ImageField, ListField, IntegerField, FloatField)
from django.db import models
import ldapdb.models
import ldap

LDAP_BASE_DN = 'ou=FCS,o=BUT,c=pl'
LDAP_ORGANIZATIONAL_UNIT_HEAD_NODE = 'cn=kierownik'
LDAP_ORGANIZATIONAL_UNIT_EMPLOYEES_NODE = 'cn=pracownicy'

class LdapStudent(ldapdb.models.Model):
    u'''
    Student
    '''
    # LDAP meta-data
    base_dn = "%s,%s" % ('ou=students,ou=people', LDAP_BASE_DN)
    object_classes = ['posixAccount', 'inetOrgPerson']

    username = CharField(db_column='uid', primary_key=True)
    uid = IntegerField(db_column='uidNumber', unique=True)

    firstName = CharField(db_column='givenName')
    lastName = CharField(db_column='sn')
    fullName = CharField(db_column='cn')
    email = CharField(db_column='mail')

    def __unicode__(self):
        return '%s %s' % (self.username, self.fullName)

class LdapOrganization(ldapdb.models.Model):
    u'''
    Organizacja
    '''
    # LDAP meta-data
    base_dn = "%s,%s" % ('ou=organizations,ou=people', LDAP_BASE_DN)
    object_classes = ['organizationalPerson']

    username = CharField(db_column='uid', primary_key=True)
    # nazwa organizacji
    name = CharField(db_column='cn')

    # dane osoby reprezentującej organizację
    representantFirstName = CharField(db_column='givenName')
    representantLastName = CharField(db_column='sn')
    representantEmail = CharField(db_column='mail')

    def __unicode__(self):
        return '%s, %s %s' % (self.name, self.representantFirstName, self.representantLastName)

class LdapEmployee(ldapdb.models.Model):
    u'''
    Pracownik
    '''
    # LDAP meta-data
    base_dn = "%s,%s" % ('ou=employees,ou=people', LDAP_BASE_DN)
    object_classes = ['organizationalPerson', 'person', 'inetOrgPerson']

    username = CharField(db_column='uid', primary_key=True)

    firstName = CharField(db_column='givenName')
    lastName = CharField(db_column='sn')
    fullName = CharField(db_column='cn')
    email = CharField(db_column='mail')

    # tytuł naukowy
    title = CharField(db_column='title')
    # stanowisko pracy (asystent, adiunkt, itp.)
    position = CharField(db_column='employeeType')

    def __getattr__(self, name):
        if name == 'organizationalUnit':
            return self.__getOrganizationalUnit()
        else:
            raise AttributeError(name)

    # self.organizationalUnit : LdapOrganizationalUnit
    # katedra, dziekanat, itp.
    def __getOrganizationalUnit(self):
        result = None

        organizationalUnits = LdapOrganizationalUnit.objects.all()
        for unit in organizationalUnits:
            if self in unit.employees:
                result = unit
                break

        return result

    # nadpisany operator porównania
    def __eq__(self, other):
        # sprawdzanie zgodności 'uid' z LDAPa
        return self.username == other.username

    def __unicode__(self):
        return '%s %s' % (self.title, self.fullName)

class LdapStudyCycle(ldapdb.models.Model):
    u'''
    Cykl ksztalcenia
    '''
    # LDAP meta-data
    base_dn = "%s,%s" % ('ou=studycycles', LDAP_BASE_DN)
    search_scope = ldap.SCOPE_ONELEVEL;

    name = CharField(db_column='cn', primary_key=True)
    
    # lista DN studentów realizujących dany cykl
    studentsDnList = ListField(db_column='member')

    def __getattr__(self, name):
        if name == 'students':
            return self.getStudents()
        else:
            raise AttributeError(name)

    # self.students : Lista<LdapStudent>
    # lista studentów
    def getStudents(self):
        result = []
        for studentDn in self.studentsDnList:
            result += LdapStudent.scoped(studentDn).objects.all()
        return result

    def __unicode__(self):
        return self.name

class LdapOrganizationalUnit(ldapdb.models.Model):
    u'''
    Jednostka organizacyjna
    '''
    # LDAP meta-data
    base_dn = "%s,%s" % ('ou=units', LDAP_BASE_DN)
    object_classes = ['organizationalUnit']
    search_scope = ldap.SCOPE_ONELEVEL

    # skrócona nazwa, klucz w LDAP
    ou = CharField(db_column='ou', primary_key=True)
    name = CharField(db_column='description')

    def __getattr__(self, name):
        if name == 'head':
            return self.__getHead()
        elif name == 'employees':
            return self.__getEmployees()
        else:
            raise AttributeError(name)

    # self.head : LdapEmployee
    # kierownik jednostki
    def __getHead(self):
        headRole = LdapOrganizationalRole.scoped('%s,%s' % (LDAP_ORGANIZATIONAL_UNIT_HEAD_NODE, self.dn)).objects.first()
        if headRole is not None:
            return headRole.occupant
        else:
            return None
    
    # self.employees : Lista<LdapEmployee>
    # pracownicy jednostki
    def __getEmployees(self):
        scopedModel = LdapOrganizationalMemebersGroup.scoped('%s,%s' % (LDAP_ORGANIZATIONAL_UNIT_EMPLOYEES_NODE, self.dn))
        # pozyskanie grupy pracowników jako listy DN
        employeesGroup = scopedModel.objects.first()

        result = []
        for employeeDn in employeesGroup.members:
            # pobieranie odpowiedniego LdapEmployee i dodanie do listy
            result += LdapEmployee.scoped(employeeDn).objects.all()
        return result

    def __unicode__(self):
        return self.name

class LdapOrganizationalRole(ldapdb.models.Model):
    u'''
    Rola w jednostce organizacyjnej
    '''
    # LDAP meta-data
    object_classes = ['organizationalRole']

    name = CharField(db_column='cn', primary_key=True)
    occupantDn = CharField(db_column='roleOccupant')

    def __getattr__(self, name):
        if name == 'occupant':
            return self.getOccupant()
        else:
            raise AttributeError(name)

    # self.occupant : LdapEmployee
    # osoba pełniąca daną rolę
    def getOccupant(self):
        return LdapEmployee.scoped(self.occupantDn).objects.first()

    def __unicode__(self):
        return '%s => %s' % (self.name, self.occupant)

class LdapOrganizationalMemebersGroup(ldapdb.models.Model):
    u'''
    Członkowie jednostki organizacyjnej
    '''
    # LDAP meta-data
    object_classes = ['groupOfNames']

    name = CharField(db_column='cn', primary_key=True)
    members = ListField(db_column='member')

    def __unicode__(self):
        return self.name

class LdapAuthorities(object):
    u'''
    Władze wydziału
    '''

    base_dn = "%s,%s" % ('ou=authorities', LDAP_BASE_DN)

    DEAN = 'dean'
    VICE_DEAN_FOR_PROMOTION = 'vice-dean-promotion'
    VICE_DEAN_FOR_RESEARCH = 'vice-dean-science'
    VICE_DEAN_FOR_STUDENTS = 'vice-dean-students'

    # przedstawiciel władz : LdapEmployee
    @classmethod
    def getAuthority(cls, name):
        scopedModel = LdapOrganizationalRole.scoped('cn=%s,%s' % (name, cls.base_dn))
        role = scopedModel.objects.first()
        if role is not None:
            return role.getOccupant()
        else:
            raise DoesNotExist(name)

class DoesNotExist(Exception):
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return "%s does not exist." % (self.value)