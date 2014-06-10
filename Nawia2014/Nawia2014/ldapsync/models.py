# -*- coding: utf-8 -*-

u''' @package ldapsync.models
Moduł gromadzący wszystkie modele opisujące dane przechowywane w bazie LDAP.

Modele LdapXxx są wykorzystywane przez moduł ldapsync.ldapsync do synchronizowania
lokalnej, relacyjnej bazy danych z bazą LDAP.
'''

from ldapdb.models.fields import (CharField, ImageField, ListField, IntegerField, FloatField)
from django.db import models
import ldapdb.models
import ldap

### Bazowe Distinguished Name dla wszystkich modeli LdapXxx
LDAP_BASE_DN = 'ou=FCS,o=BUT,c=pl'
### Nazwa węzła zawierającego kierownika jednostki organizacyjnej
LDAP_ORGANIZATIONAL_UNIT_HEAD_NODE = 'cn=kierownik'
### Nazwa węzła zawierającego pracowników jednostki organizacyjnej
LDAP_ORGANIZATIONAL_UNIT_EMPLOYEES_NODE = 'cn=pracownicy'

class LdapStudent(ldapdb.models.Model):
    u'''
    Reprezentuje studenta zarejestrowanego w bazie LDAP.
    '''
    ### metadane LDAP
    base_dn = "%s,%s" % ('ou=students,ou=people', LDAP_BASE_DN)
    ### metadane LDAP
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
    Reprezentuje organizację zarejestrowaną w bazie LDAP.
    '''
    ### metadane LDAP
    base_dn = "%s,%s" % ('ou=organizations,ou=people', LDAP_BASE_DN)
    ### metadane LDAP
    object_classes = ['organizationalPerson']

    username = CharField(db_column='uid', primary_key=True)
    ### nazwa organizacji
    name = CharField(db_column='cn')

    ### imię osoby reprezentującej organizację
    representantFirstName = CharField(db_column='givenName')
    ### nazwisko osoby reprezentującej organizację
    representantLastName = CharField(db_column='sn')
    ### email osoby reprezentującej organizację
    representantEmail = CharField(db_column='mail')

    def __unicode__(self):
        return '%s, %s %s' % (self.name, self.representantFirstName, self.representantLastName)

class LdapEmployee(ldapdb.models.Model):
    u'''
    Reprezentuje pracownika zarejestrowanego w bazie LDAP.
    '''
    ### metadane LDAP
    base_dn = "%s,%s" % ('ou=employees,ou=people', LDAP_BASE_DN)
    ### metadane LDAP
    object_classes = ['organizationalPerson', 'person', 'inetOrgPerson']

    username = CharField(db_column='uid', primary_key=True)

    firstName = CharField(db_column='givenName')
    lastName = CharField(db_column='sn')
    fullName = CharField(db_column='cn')
    email = CharField(db_column='mail')

    ### tytuł naukowy
    title = CharField(db_column='title')
    ### stanowisko pracy (asystent, adiunkt, itp.)
    position = CharField(db_column='employeeType')

    def __getattr__(self, name):
        u'''
        Zapewnia przekierowanie wywołań atrybutu LdapEmployee.organizationalUnit
        na wywołania metody LdapEmployee.__getOrganizationalUnit().
        '''
        if name == 'organizationalUnit':
            return self.__getOrganizationalUnit()
        else:
            raise AttributeError(name)

    # self.organizationalUnit : LdapOrganizationalUnit
    def __getOrganizationalUnit(self):
        u'''
        Getter dla atrybutu LdapEmployee.organizationalUnit,
        zwracający jednostkę organizacyjną tego pracownika (katedra, dziekanat, itp.).
        Odwoływać się poprzez LdapEmployee.organizationalUnit (nadpisano LdapEmployee.__getattr__()).
        @returns LdapOrganizationalUnit
        '''
        result = None

        organizationalUnits = LdapOrganizationalUnit.objects.all()
        for unit in organizationalUnits:
            if self in unit.employees:
                result = unit
                break

        return result

    ### Nadpisany operator porównania.
    def __eq__(self, other):
        # sprawdzanie zgodności 'uid' z LDAPa
        return self.username == other.username

    def __unicode__(self):
        return '%s %s' % (self.title, self.fullName)

class LdapStudyCycle(ldapdb.models.Model):
    u'''
    Reprezentuje cykl ksztalcenia zarejestrowany w bazie LDAP.
    '''
    ### metadane LDAP
    base_dn = "%s,%s" % ('ou=studycycles', LDAP_BASE_DN)
    ### metadane LDAP
    search_scope = ldap.SCOPE_ONELEVEL;

    name = CharField(db_column='cn', primary_key=True)
    
    ### lista DN studentów realizujących dany cykl
    studentsDnList = ListField(db_column='member')

    def __getattr__(self, name):
        u'''
        Zapewnia przekierowanie wywołań atrybutu LdapStudyCycle.students
        na wywołania metody LdapStudyCycle.getStudents().
        '''
        if name == 'students':
            return self.getStudents()
        else:
            raise AttributeError(name)

    # self.students : Lista<LdapStudent>
    def getStudents(self):
        u'''
        Getter dla atrybutu LdapStudyCycle.students, zwracający listę studentów tego cyklu kształcenia.
        Odwoływać się poprzez LdapStudyCycle.students (nadpisano LdapStudyCycle.__getattr__()).
        @returns [LdapStudent] lista studentów
        '''
        result = []
        for studentDn in self.studentsDnList:
            result += LdapStudent.scoped(studentDn).objects.all()
        return result

    def __unicode__(self):
        return self.name

class LdapOrganizationalUnit(ldapdb.models.Model):
    u'''
    Reprezentuje jednostkę organizacyjną zarejestrowaną w bazie LDAP.
    '''
    ### metadane LDAP
    base_dn = "%s,%s" % ('ou=units', LDAP_BASE_DN)
    ### metadane LDAP
    object_classes = ['organizationalUnit']
    ### metadane LDAP
    search_scope = ldap.SCOPE_ONELEVEL

    ### skrócona nazwa
    ou = CharField(db_column='ou', primary_key=True)
    ### klucz w LDAP
    name = CharField(db_column='description')

    def __getattr__(self, name):
        u'''
        Zapewnia przekierowanie wywołań atrybutów LdapOrganizationalUnit.head i LdapOrganizationalUnit.employees
        na wywołania metod LdapOrganizationalUnit.__getHead() i LdapOrganizationalUnit.__getEmployees().
        '''
        if name == 'head':
            return self.__getHead()
        elif name == 'employees':
            return self.__getEmployees()
        else:
            raise AttributeError(name)

    # self.head : LdapEmployee
    def __getHead(self):
        u'''
        Getter dla atrybutu LdapOrganizationalUnit.head, zwracający kierownika tej jednostki organizacyjnej.
        Odwoływać się poprzez LdapOrganizationalUnit.head (nadpisano LdapOrganizationalUnit.__getattr__()).
        @returns LdapEmployee kierownik jednostki
        '''
        headRole = LdapOrganizationalRole.scoped('%s,%s' % (LDAP_ORGANIZATIONAL_UNIT_HEAD_NODE, self.dn)).objects.first()
        if headRole is not None:
            return headRole.occupant
        else:
            return None
    
    # self.employees : Lista<LdapEmployee>
    def __getEmployees(self):
        u'''
        Getter dla atrybutu LdapOrganizationalUnit.employees, zwracający listę pracowników tej jednostki organizacyjnej.
        Odwoływać się poprzez LdapOrganizationalUnit.employees (nadpisano LdapOrganizationalUnit.__getattr__()).
        @returns [LdapEmployee] pracownicy jednostki
        '''
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
    Przypisuje pracownikowi uczelni rolę w jednostce organizacyjnej. Reprezentuje wpis w bazie LDAP.
    '''
    ### metadane LDAP
    object_classes = ['organizationalRole']

    name = CharField(db_column='cn', primary_key=True)
    occupantDn = CharField(db_column='roleOccupant')

    def __getattr__(self, name):
        u'''
        Zapewnia przekierowanie wywołań atrybutu LdapOrganizationalRole.occupant
        na wywołania metody LdapOrganizationalRole.getOccupant().
        '''
        if name == 'occupant':
            return self.getOccupant()
        else:
            raise AttributeError(name)

    # self.occupant : LdapEmployee
    def getOccupant(self):
        u'''
        Getter dla atrybutu LdapOrganizationalRole.occupant, zwracający pracownika pełniącego tę rolę
        w jednostce organizacyjnej.
        Odwoływać się poprzez LdapOrganizationalRole.occupant (nadpisano LdapOrganizationalRole.__getattr__()).
        @returns LdapEmployee osoba pełniąca daną rolę
        '''
        return LdapEmployee.scoped(self.occupantDn).objects.first()

    def __unicode__(self):
        return '%s => %s' % (self.name, self.occupant)

class LdapOrganizationalMemebersGroup(ldapdb.models.Model):
    u'''
    Reprezentuje członków jednostki organizacyjnej.
    '''
    ### metadane LDAP
    object_classes = ['groupOfNames']

    name = CharField(db_column='cn', primary_key=True)
    members = ListField(db_column='member')

    def __unicode__(self):
        return self.name

class LdapAuthorities(object):
    u'''
    Klasa pomocnicza, pozwalająca pobrać z bazy LDAP dane o jednym z pracowników pełniących rolę władz wydziału.
    '''

    base_dn = "%s,%s" % ('ou=authorities', LDAP_BASE_DN)

    ### Nazwa roli w bazie LDAP: Dziekan.
    DEAN = 'dean'
    ### Nazwa roli w bazie LDAP: Prodziekan ds. Promocji i Współpracy.
    VICE_DEAN_FOR_PROMOTION = 'vice-dean-promotion'
    ### Nazwa roli w bazie LDAP: Prodziekan ds. Nauki.
    VICE_DEAN_FOR_RESEARCH = 'vice-dean-science'
    ### Nazwa roli w bazie LDAP: Prodziekan ds. Studenckich i Dydaktyki.
    VICE_DEAN_FOR_STUDENTS = 'vice-dean-students'

    @classmethod
    def getAuthority(cls, name):
        u'''
        Zwraca przedstawiciela władz wydziału pełniącego daną rolę.

        @param name nazwa roli w bazie LDAP
        @returns LdapEmployee
        '''
        scopedModel = LdapOrganizationalRole.scoped('cn=%s,%s' % (name, cls.base_dn))
        role = scopedModel.objects.first()
        if role is not None:
            return role.getOccupant()
        else:
            raise DoesNotExist(name)

class DoesNotExist(Exception):
    u'''
    Wyjątek wyrzucany wtedy, gdy w bazie LDAP nie odnaleziono szukanego obiektu.
    '''
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return "%s does not exist." % (self.value)