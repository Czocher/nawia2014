# -*- coding: utf-8 -*-
u'''
Moduł zapewniający funkcje synchronizujące lokalną bazę danych z bazą LDAP.

Podczas synchronizacji dane w bazie powinny zostać uznane za niespójne,
tzn. serwis powinien być chwilowo niedostępny z zewnątrz.
'''
import pytz
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from models import LdapStudent, LdapEmployee, LdapStudyCycle
from nawia.models import Student, Employee, StudyCycle

class LdapSync:
    @classmethod
    def sync(cls):
        cls.__syncStudents()
        #cls.__syncEmployees()
        cls.__syncStudyCycles()

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
                print 'User and Student already existed'
            except Student.DoesNotExist:
                try:
                    localUser = User.objects.get(username=ldapStudent.username)
                    print 'User already existed'
                except User.DoesNotExist:
                    #TODO: być może last_login powinien być ustawiany na bardziej logiczną wartość, np. None
                    #      (w tej chwili niemożliwe, bo pole jest wymagane).
                    localUser = User(
                                     username=ldapStudent.username,
                                     last_login=datetime(1970, 1, 1, tzinfo=pytz.utc),
                                     date_joined=timezone.now())
                    print 'Created a new User'
                localStudent = Student()
                print 'Created a new Student'

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
                print 'StudyCycle already existed'
            except StudyCycle.DoesNotExist:
                localStudyCycle = StudyCycle(ldapId=ldapStudyCycle.name, name=ldapStudyCycle.name)
                print 'Created a new StudyCycle'

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
