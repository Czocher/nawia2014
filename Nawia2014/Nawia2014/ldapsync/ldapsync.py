# -*- coding: utf-8 -*-
import pytz
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from models import LdapStudent, LdapStudyCycle, LdapEmployee, LdapOrganizationalUnit, LdapOrganization, LdapAuthorities
from models import DoesNotExist as ldapModels_DoesNotExist
from nawia.models import Student, StudyCycle, Employee, OrganizationalUnit, Organization, Authority
from collections import namedtuple

class LdapSync:
    u'''
    Klasa zapewniająca funkcje synchronizujące lokalną bazę danych z bazą LDAP.

    Podczas synchronizacji dane w bazie powinny zostać uznane za niespójne,
    tzn. serwis powinien być chwilowo niedostępny z zewnątrz.
    '''
    @classmethod
    def sync(cls):
        cls.__syncStudents()
        cls.__syncStudyCycles()
        cls.__syncEmployees()
        cls.__syncOrganizationalUnits()
        cls.__syncOrganizations()
        cls.__syncAuthorities()

    @classmethod
    def __syncStudents(cls):
        u'''
        Synchronizuje bazę obiektów Student z zewnętrzną bazą LDAP (modele LdapStudent).
        Uwaga - zrywane są zależności z klucza obcego Student.studyCycle.
        Ustawiona flaga Student.isLdapSynced oznacza jedynie, że zsynchronizowane są dane osobowe studenta:
        imię, nazwisko i email. Pozostałe pola są nullowane, aby przygotować je do następnych
        etapów synchronizacji (jak np. __syncStudyCycles()).
        '''
        #oznacz wszystkie obiekty Student jako niezsynchronizowane z LDAPem
        for localStudent in Student.objects.all():
            #usuń powiązania ze StudyCycle, żeby przygotować obiekty do synchronizacji cyklów kształcenia
            localStudent.studyCycles.clear()
            localStudent.isLdapSynced = False
            localStudent.save()
        #aktualizuj wszystkie lokalne obiekty Student, które są odzwierciedlone w LDAPie;
        # jeśli któregoś Studenta tam nie ma, to pozostanie on oznaczony flagą isLdapSynced == False
        for ldapStudent in LdapStudent.objects.all():
            localUser = None
            localStudent = None
            try:
                localStudent = Student.objects.get(user__username=ldapStudent.username)
                localUser = localStudent.user
                #^User i Student istnieli już wcześniej
            except Student.DoesNotExist:
                try:
                    localUser = User.objects.get(username=ldapStudent.username)
                    #^User istniał już wcześniej
                except User.DoesNotExist:
                    #TODO: być może last_login powinien być ustawiany na bardziej logiczną wartość, np. None
                    #      (w tej chwili niemożliwe, bo pole jest wymagane).
                    localUser = User(
                                     username=ldapStudent.username,
                                     last_login=datetime(1970, 1, 1, tzinfo=pytz.utc),
                                     date_joined=timezone.now())
                    #^utworzono nowego Usera
                localStudent = Student()
                #^utworzono nowego Studenta

            localUser.first_name = ldapStudent.firstName
            localUser.last_name = ldapStudent.lastName
            localUser.email = ldapStudent.email
            localUser.save()
            localStudent.user = localUser
            localStudent.isLdapSynced = True
            localStudent.save()

    @classmethod
    def __syncStudyCycles(cls):
        u'''
        Synchronizuje bazę obiektów StudyCycle z zewnętrzną bazą LDAP (modele LdapStudyCycle).
        Uwaga - wymaga przygotowania obiektów Student: muszą być wcześniej zsynchronizowane z bazą LDAP,
        a ich referencje na obiekty StudyCycle muszą być wyczyszczone (zostaną odtworzone na tym etapie synchronizacji).
        '''
        #oznacz wszystkie obiekty StudyCycle jako niezsynchronizowane z LDAPem
        for localStudyCycle in StudyCycle.objects.all():
            localStudyCycle.isLdapSynced = False
            localStudyCycle.save()
        #aktualizuj wszystkie lokalne obiekty StudyCycle, które mają swoje kopie w LDAPie;
        #jeśli któryś StudyCycle nie istnieje w LDAP, to w bazie pozostanie oznaczony flagą isLdapSynced == False
        for ldapStudyCycle in LdapStudyCycle.objects.all():
            localStudyCycle = None
            try:
                localStudyCycle = StudyCycle.objects.get(ldapId=ldapStudyCycle.name)
                #^StudyCycle istniał już wcześniej
            except StudyCycle.DoesNotExist:
                localStudyCycle = StudyCycle(ldapId=ldapStudyCycle.name, name=ldapStudyCycle.name)
                #^utworzono nowy StudyCycle

            localStudyCycle.isLdapSynced = True
            localStudyCycle.save()

            #zaktualizuj przynależność studentów należących do tego StudyCycle
            for ldapStudent in ldapStudyCycle.students:
                try:
                    localStudent = Student.objects.get(user__username=ldapStudent.username)
                    localStudent.studyCycles.add(localStudyCycle)
                    localStudent.save()
                except Student.DoesNotExist:
                    #TODO: co zrobić, jeśli student występuje w cyklu, ale nie ma go nigdzie indziej? Błąd? Log? Zignorować po cichu?
                    pass

    @classmethod
    def __syncEmployees(cls):
        u'''
        Synchronizuje bazę obiektów Employee z zewnętrzną bazą LDAP (modele LdapEmployee).
        Uwaga - zrywane są zależności z klucza obcego Employee.organizationalUnit.
        Ustawiona flaga Employee.isLdapSynced oznacza jedynie, że zsynchronizowane są dane osobowe pracownika:
        imię, nazwisko, email, tytuł naukowy i stanowisko. Pozostałe pola są nullowane, aby przygotować je do następnych
        etapów synchronizacji (jak np. __syncOrganizationalUnits()).
        '''
        #oznacz wszystkie obiekty Employee jako niezsynchronizowane z LDAPem
        for localEmployee in Employee.objects.all():
            #usuń powiązania z OrganizationalUnit, żeby przygotować obiekty do synchronizacji jednostek organizacyjnych
            #TODO: czy .organizationalUnit.clear() działa jak powinno?
            localEmployee.organizationalUnit = None
            localEmployee.isLdapSynced = False
            localEmployee.save()
        #aktualizuj wszystkie lokalne obiekty Employee, które są odzwierciedlone w LDAPie;
        # jeśli któregoś Employee tam nie ma, to pozostanie on oznaczony flagą isLdapSynced == False
        for ldapEmployee in LdapEmployee.objects.all():
            localUser = None
            localEmployee = None
            try:
                localEmployee = Employee.objects.get(user__username=ldapEmployee.username)
                localUser = localEmployee.user
                #^User i Employee istnieli już wcześniej
            except Employee.DoesNotExist:
                try:
                    localUser = User.objects.get(username=ldapEmployee.username)
                    #^User istniał już wcześniej
                except User.DoesNotExist:
                    #TODO: być może last_login powinien być ustawiany na bardziej logiczną wartość, np. None
                    #      (w tej chwili niemożliwe, bo pole jest wymagane).
                    localUser = User(
                                     username=ldapEmployee.username,
                                     last_login=datetime(1970, 1, 1, tzinfo=pytz.utc),
                                     date_joined=timezone.now())
                    #^utworzono nowego Usera
                localEmployee = Employee()
                #^utworzono nowego Employee

            localUser.first_name = ldapEmployee.firstName
            localUser.last_name = ldapEmployee.lastName
            localUser.email = ldapEmployee.email
            localUser.save()
            localEmployee.user = localUser
            localEmployee.title = ldapEmployee.title
            localEmployee.position = ldapEmployee.position
            localEmployee.isLdapSynced = True
            localEmployee.save()

    @classmethod
    def __syncOrganizationalUnits(cls):
        u'''
        Synchronizuje bazę obiektów OrganizationalUnit z zewnętrzną bazą LDAP (modele LdapOrganizationalUnit).
        Uwaga - wymaga przygotowania obiektów Employee: muszą być wcześniej zsynchronizowane z bazą LDAP,
        a ich referencje na obiekty OrganizationalUnit muszą być wyczyszczone (zostaną odtworzone na tym etapie synchronizacji).
        '''
        #oznacz wszystkie obiekty OrganizationalUnit jako niezsynchronizowane z LDAPem
        for localOrganizationalUnit in OrganizationalUnit.objects.all():
            localOrganizationalUnit.isLdapSynced = False
            localOrganizationalUnit.save()
        #aktualizuj wszystkie lokalne obiekty OrganizationalUnit, które mają swoje kopie w LDAPie;
        #jeśli któraś OrganizationalUnit nie istnieje w LDAP, to w bazie pozostanie oznaczona flagą isLdapSynced == False
        for ldapOrganizationalUnit in LdapOrganizationalUnit.objects.all():
            localOrganizationalUnit = None
            try:
                localOrganizationalUnit = OrganizationalUnit.objects.get(ldapId=ldapOrganizationalUnit.name)
                #^OrganizationalUnit istniała już wcześniej
            except OrganizationalUnit.DoesNotExist:
                localOrganizationalUnit = OrganizationalUnit(
                                                             ldapId=ldapOrganizationalUnit.name,
                                                             name=ldapOrganizationalUnit.name)
                #^utworzono nową OrganizationalUnit

            #przypisz kierownika jednostki
            try:
                localOrganizationalUnit.head = Employee.objects.get(user__username=ldapOrganizationalUnit.head.username)
            except:
                #może nie być zdefiniowany, wtedy zignoruj wyjątek
                pass
            localOrganizationalUnit.isLdapSynced = True
            localOrganizationalUnit.save()

            #zaktualizuj przynależność pracowników należących do tej OrganizationalUnit
            for ldapEmployee in ldapOrganizationalUnit.employees:
                try:
                    localEmployee = Employee.objects.get(user__username=ldapEmployee.username)
                    localEmployee.organizationalUnit = localOrganizationalUnit
                    localEmployee.save()
                except Employee.DoesNotExist:
                    #TODO: co zrobić, jeśli pracownik występuje jako członek jednostki, ale nie ma go nigdzie indziej? Błąd? Log? Zignorować po cichu?
                    pass

    @classmethod
    def __syncOrganizations(cls):
        u'''
        Synchronizuje bazę obiektów Organization z zewnętrzną bazą LDAP (modele LdapOrganization).
        '''
        #oznacz wszystkie obiekty Organization jako niezsynchronizowane z LDAPem
        for localOrganization in Organization.objects.all():
            localOrganization.isLdapSynced = False
            localOrganization.save()
        #aktualizuj wszystkie lokalne obiekty Organization, które są odzwierciedlone w LDAPie;
        # jeśli którejś Organization tam nie ma, to pozostanie ona oznaczona flagą isLdapSynced == False
        for ldapOrganization in LdapOrganization.objects.all():
            localUser = None
            localOrganization = None
            try:
                localOrganization = Organization.objects.get(user__username=ldapOrganization.username)
                localUser = localOrganization.user
                #^User i Organization istnieli już wcześniej
            except Organization.DoesNotExist:
                try:
                    localUser = User.objects.get(username=ldapOrganization.username)
                    #^User istniał już wcześniej
                except User.DoesNotExist:
                    #TODO: być może last_login powinien być ustawiany na bardziej logiczną wartość, np. None
                    #      (w tej chwili niemożliwe, bo pole jest wymagane).
                    localUser = User(
                                     username=ldapOrganization.username,
                                     last_login=datetime(1970, 1, 1, tzinfo=pytz.utc),
                                     date_joined=timezone.now())
                    #^utworzono nowego Usera
                localOrganization = Organization()
                #^utworzono nową Organization

            localUser.first_name = ldapOrganization.representantFirstName
            localUser.last_name = ldapOrganization.representantLastName
            localUser.email = ldapOrganization.representantEmail
            localUser.save()
            localOrganization.user = localUser
            localOrganization.name = ldapOrganization.name
            localOrganization.isLdapSynced = True
            localOrganization.save()

    @classmethod
    def __syncAuthorities(cls):
        u'''
        Synchronizuje bazę obiektów Authority z zewnętrzną bazą LDAP (klasa pomocnicza LdapAuthorities).
        '''
        #typ RoleTuple - używać podobnie jak zwykłą krotkę, ale z zawartością dostępną poprzez atrybuty .ldap i .local
        RoleTuple = namedtuple('RoleTuple', ('ldapName', 'localName'))
        #odpowiadające sobie nazwy ról w bazie LDAP i w bazie lokalnej
        authorityRoles = (
            RoleTuple(LdapAuthorities.DEAN, Authority.DEAN),
            RoleTuple(LdapAuthorities.VICE_DEAN_FOR_PROMOTION, Authority.VICE_DEAN_FOR_PROMOTION),
            RoleTuple(LdapAuthorities.VICE_DEAN_FOR_RESEARCH, Authority.VICE_DEAN_FOR_RESEARCH),
            RoleTuple(LdapAuthorities.VICE_DEAN_FOR_STUDENTS, Authority.VICE_DEAN_FOR_STUDENTS),
        )
        #usuń obiekty Authority o rolach nieznanych systemowi
        Authority.objects.exclude(role__in = [role.localName for role in authorityRoles]).delete()
        
        #aktualizuj wszystkie lokalne obiekty Authority, które są odzwierciedlone w LDAPie
        for role in authorityRoles:
            ldapAuthority = None
            localAuthority = None
            try:
                ldapAuthority = LdapAuthorities.getAuthority(role.ldapName)
                localAuthority = Authority.objects.get(role=role.localName)
                #^Authority o tej roli istnieje w LDAPie i w lokalnej bazie
            except Authority.DoesNotExist:
                localAuthority = Authority(role=role.localName)
                #^utworzono nowe Authority
            except ldapModels_DoesNotExist:
                #Authority o tej roli nie istnieje w LDAPie
                #TODO: jeśli dzieje się coś takiego, to prawdopodobnie jest niespójność między modelami LDAP a bazą LDAP!
                try:
                    #usuń pracownika z lokalnego Authority, jeśli istnieje
                    localAuthority = Authority.objects.get(role=role.localName)
                    localAuthority.occupant = None
                    localAuthority.save()
                    #^usunięto pracownika z bieżącego Authority
                except Authority.DoesNotExist:
                    #jeśli nie istnieje - utwórz, ale z pustym polem [occupant]
                    localAuthority = Authority(role=role.localName)
                    localAuthority.save()
                #pomiń resztę ciała pętli, bo wszystkie potrzebne zmiany dla tej roli zostały już poczynione
                continue
                
            #przypisz pracownika pełniącego tę rolę
            localAuthority.occupant = Employee.objects.get(user__username=ldapAuthority.username)
            localAuthority.save()