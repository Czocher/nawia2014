# -*- coding: utf-8 -*-

u''' @package ldapsync.ldapsync
Moduł zapewniający funkcje synchronizujące lokalną bazę danych z bazą LDAP i przydzielające uprawnienia użytkownikom.

Podczas synchronizacji dane w bazie powinny zostać uznane za niespójne,
tzn. serwis powinien być chwilowo niedostępny z zewnątrz.

LdapSync.sync() metoda przeprowadza pełną synchronizację.
'''

import pytz
import logging
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q
from models import LdapStudent, LdapStudyCycle, LdapEmployee, LdapOrganizationalUnit, LdapOrganization, LdapAuthorities
from models import DoesNotExist as ldapModels_DoesNotExist
from faculty.models import Student, StudyCycle, Employee, OrganizationalUnit, Organization, Authority
from collections import namedtuple
import permissions

class LdapSync:
    u'''
    Klasa zapewniająca funkcje synchronizujące lokalną bazę danych z bazą LDAP.

    Podczas synchronizacji dane w bazie powinny zostać uznane za niespójne,
    tzn. serwis powinien być chwilowo niedostępny z zewnątrz.
    '''

    class InstancesCounter:
        def __init__(self):
            self.created = 0
            self.deleted = 0
            self.synced = 0
            self.nonSynced = 0


    @classmethod
    def sync(cls, logger=None):
        u'''
        Metoda wykonująca wszystkie kroki synchronizacji we właściwej kolejności.
        Przez parametr 'logger' można przekazać instancję loggera - w przeciwnym razie
        zostanie użyta domyślna instancja zwracana przez logging.getLogger(__name__).
        '''
        if not logger:
            logger = logging.getLogger(__name__)
        if len(logger.handlers) == 0:
            logger.addHandler(logging.NullHandler())
        
        permissions.prepareForSync()

        logger.info(u'Synchronizacja studentów...')
        cls.__syncStudents(logger)
        logger.info(u'Synchronizacja cyklów kształcenia...')
        cls.__syncStudyCycles(logger)
        logger.info(u'Synchronizacja pracowników...')
        cls.__syncEmployees(logger)
        logger.info(u'Synchronizacja jednostek organizacyjnych...')
        cls.__syncOrganizationalUnits(logger)
        logger.info(u'Synchronizacja organizacji...')
        cls.__syncOrganizations(logger)
        logger.info(u'Synchronizacja władz wydziału...')
        cls.__syncAuthorities(logger)
        logger.info(u'Synchronizacja zakończona.')


    @classmethod
    def __syncStudents(cls, logger):
        u'''
        Synchronizuje bazę obiektów Student z zewnętrzną bazą LDAP (modele LdapStudent).
        Uwaga - zrywane są zależności z klucza obcego Student.studyCycle.
        Ustawiona flaga Student.isLdapSynced oznacza jedynie, że zsynchronizowane są dane osobowe studenta:
        imię, nazwisko i email. Pozostałe pola są nullowane, aby przygotować je do następnych
        etapów synchronizacji (jak np. __syncStudyCycles()).
        '''
        studentsCounter = cls.InstancesCounter()
        usersCounter = cls.InstancesCounter()

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
                logger.debug(u'W bazie odnaleziono użytkownika "%s" z powiązanym obiektem Student.', ldapStudent.username)
            except Student.DoesNotExist:
                try:
                    localUser = User.objects.get(username=ldapStudent.username)
                    logger.info(u'Użytkownik "%s" istnieje w bazie, jednak nie ma przypisanego obiektu Student.', ldapStudent.username)
                except User.DoesNotExist:
                    #TODO: być może last_login powinien być ustawiany na bardziej logiczną wartość, np. None
                    #      (w tej chwili niemożliwe, bo pole jest wymagane).
                    localUser = User(
                                     username=ldapStudent.username,
                                     last_login=datetime(1970, 1, 1, tzinfo=pytz.utc),
                                     date_joined=timezone.now())
                    logger.info(u'Utworzono nowego użytkownika "%s".', localUser.username)
                    usersCounter.created += 1
                localStudent = Student()
                logger.info(u'Utworzono nowy obiekt Student dla użytkownika "%s".', ldapStudent.username)
                studentsCounter.created += 1

            localUser.first_name = ldapStudent.firstName
            localUser.last_name = ldapStudent.lastName
            localUser.email = ldapStudent.email
            localUser.save()
            logger.debug(u'Zaktualizowano dane w obiekcie User: username="%s", pk="%s".', localUser.username, localUser.pk)
            usersCounter.synced += 1
            localStudent.user = localUser
            localStudent.isLdapSynced = True
            localStudent.save()
            permissions.registerStudent(localStudent)
            logger.debug(u'Zaktualizowano dane w obiekcie Student: user.username="%s" pk="%s".', localStudent.user.username, localStudent.pk)
            studentsCounter.synced += 1
        
        studentsCounter.nonSynced = Student.objects.filter(isLdapSynced=False).count()
        logger.info(
            u'Zsynchronizowano %s obiektów Student (w tym utworzono: %s), pozostało niezsynchronizowanych: %s.',
            studentsCounter.synced, studentsCounter.created, studentsCounter.nonSynced
        )
        logger.info(
            u'Zaktualizowano dane %s użytkowników (w tym utworzono: %s)',
            usersCounter.synced, usersCounter.created
        )


    @classmethod
    def __syncStudyCycles(cls, logger):
        u'''
        Synchronizuje bazę obiektów StudyCycle z zewnętrzną bazą LDAP (modele LdapStudyCycle).
        Uwaga - wymaga przygotowania obiektów Student: muszą być wcześniej zsynchronizowane z bazą LDAP,
        a ich referencje na obiekty StudyCycle muszą być wyczyszczone (zostaną odtworzone na tym etapie synchronizacji).
        '''
        studyCyclesCounter = cls.InstancesCounter()

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
                logger.debug(u'W bazie odnaleziono cykl kształcenia "%s".', ldapStudyCycle.name)
            except StudyCycle.DoesNotExist:
                localStudyCycle = StudyCycle(ldapId=ldapStudyCycle.name, name=ldapStudyCycle.name)
                logger.info(u'Utworzono nowy cykl kształcenia "%s".', ldapStudyCycle.name)
                studyCyclesCounter.created += 1

            localStudyCycle.isLdapSynced = True
            localStudyCycle.save()
            logger.debug(u'Zaktualizowano dane w obiekcie StudyCycle: name="%s", pk="%s".', localStudyCycle.name, localStudyCycle.pk)
            studyCyclesCounter.synced += 1

            #zaktualizuj przynależność studentów należących do tego StudyCycle
            studentsCounter = cls.InstancesCounter()
            for ldapStudent in ldapStudyCycle.students:
                try:
                    localStudent = Student.objects.get(user__username=ldapStudent.username)
                    localStudent.studyCycles.add(localStudyCycle)
                    localStudent.save()
                    studentsCounter.synced += 1
                except Student.DoesNotExist:
                    logger.warn(
                        u'Student "%s" jest wymieniony w bazie LDAP jako uczestnik cyklu kształcenia "%s", '
                        u'ale nie ma go w bazie LDAP wśród studentów uczelni. '
                        u'Powiązanie cykl-student zostało zignorowane.',
                        ldapStudent.username, ldapStudyCycle.name
                    )
                    studentsCounter.nonSynced += 1
            logger.debug(
                u'Zaktualizowano zależności obiektu StudyCycle: %s studentów przypisano do cyklu, '
                u'%s studentów wymienionych w cyklu nie odnaleziono w bazie.',
                studentsCounter.synced, studentsCounter.nonSynced
            )
        logger.info(
            u'Zaktualizowano dane %s cyklów kształcenia (w tym utworzono: %s)',
            studyCyclesCounter.synced, studyCyclesCounter.created
        )


    @classmethod
    def __syncEmployees(cls, logger):
        u'''
        Synchronizuje bazę obiektów Employee z zewnętrzną bazą LDAP (modele LdapEmployee).
        Uwaga - zrywane są zależności z klucza obcego Employee.organizationalUnit.
        Ustawiona flaga Employee.isLdapSynced oznacza jedynie, że zsynchronizowane są dane osobowe pracownika:
        imię, nazwisko, email, tytuł naukowy i stanowisko. Pozostałe pola są nullowane, aby przygotować je do następnych
        etapów synchronizacji (jak np. __syncOrganizationalUnits()).
        '''
        employeesCounter = cls.InstancesCounter()
        usersCounter = cls.InstancesCounter()

        #oznacz wszystkie obiekty Employee jako niezsynchronizowane z LDAPem
        for localEmployee in Employee.objects.all():
            #usuń powiązania z OrganizationalUnit, żeby przygotować obiekty do synchronizacji jednostek organizacyjnych
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
                logger.debug(u'W bazie odnaleziono użytkownika "%s" z powiązanym obiektem Employee.', ldapEmployee.username)
            except Employee.DoesNotExist:
                try:
                    localUser = User.objects.get(username=ldapEmployee.username)
                    logger.info(u'Użytkownik "%s" istnieje w bazie, jednak nie ma przypisanego obiektu Employee.', ldapEmployee.username)
                except User.DoesNotExist:
                    #TODO: być może last_login powinien być ustawiany na bardziej logiczną wartość, np. None
                    #      (w tej chwili niemożliwe, bo pole jest wymagane).
                    localUser = User(
                                     username=ldapEmployee.username,
                                     last_login=datetime(1970, 1, 1, tzinfo=pytz.utc),
                                     date_joined=timezone.now())
                    logger.info(u'Utworzono nowego użytkownika "%s".', localUser.username)
                    usersCounter.created += 1
                localEmployee = Employee()
                logger.info(u'Utworzono nowy obiekt Employee dla użytkownika "%s".', ldapEmployee.username)
                employeesCounter.created += 1

            localUser.first_name = ldapEmployee.firstName
            localUser.last_name = ldapEmployee.lastName
            localUser.email = ldapEmployee.email
            localUser.save()
            logger.debug(u'Zaktualizowano dane w obiekcie User: username="%s", pk="%s".', localUser.username, localUser.pk)
            usersCounter.synced += 1
            localEmployee.user = localUser
            localEmployee.title = ldapEmployee.title
            localEmployee.position = ldapEmployee.position
            localEmployee.isLdapSynced = True
            localEmployee.save()
            permissions.registerEmployee(localEmployee)
            logger.debug(u'Zaktualizowano dane w obiekcie Employee: user.username="%s" pk="%s".', localEmployee.user.username, localEmployee.pk)
            employeesCounter.synced += 1

        employeesCounter.nonSynced = Employee.objects.filter(isLdapSynced=False).count()
        logger.info(
            u'Zsynchronizowano %s obiektów Employee (w tym utworzono: %s), pozostało niezsynchronizowanych: %s.',
            employeesCounter.synced, employeesCounter.created, employeesCounter.nonSynced
        )
        logger.info(
            u'Zaktualizowano dane %s użytkowników (w tym utworzono: %s)',
            usersCounter.synced, usersCounter.created
        )


    @classmethod
    def __syncOrganizationalUnits(cls, logger):
        u'''
        Synchronizuje bazę obiektów OrganizationalUnit z zewnętrzną bazą LDAP (modele LdapOrganizationalUnit).
        Uwaga - wymaga przygotowania obiektów Employee: muszą być wcześniej zsynchronizowane z bazą LDAP,
        a ich referencje na obiekty OrganizationalUnit muszą być wyczyszczone (zostaną odtworzone na tym etapie synchronizacji).
        '''
        organizationalUnitsCounter = cls.InstancesCounter()

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
                logger.debug(u'W bazie odnaleziono jednostkę ogranizacyjną "%s".', localOrganizationalUnit.name)
            except OrganizationalUnit.DoesNotExist:
                localOrganizationalUnit = OrganizationalUnit(
                                                             ldapId=ldapOrganizationalUnit.name,
                                                             name=ldapOrganizationalUnit.name)
                logger.info(u'Utworzono nową jednostkę ogranizacyjną "%s".', localOrganizationalUnit.name)
                organizationalUnitsCounter.created += 1

            #przypisz kierownika jednostki
            try:
                localOrganizationalUnit.head = Employee.objects.get(user__username=ldapOrganizationalUnit.head.username)
                permissions.registerDepartmentHead(localOrganizationalUnit.head)
                logger.debug(u'Przypisano kierownika jednostki organizacyjnej: "%s".', localOrganizationalUnit.head.user.username)
            except:
                logger.warn(u'W bazie nie odnaleziono kierownika jednostki organizacyjnej "%s" (szukany username: "%s").', localOrganizationalUnit.name, ldapOrganizationalUnit.head.username)
            localOrganizationalUnit.isLdapSynced = True
            localOrganizationalUnit.save()
            logger.debug(u'Zaktualizowano dane w obiekcie OrganizationalUnit: name="%s", pk="%s".', localOrganizationalUnit.name, localOrganizationalUnit.pk)
            organizationalUnitsCounter.synced += 1

            #zaktualizuj przynależność pracowników należących do tej OrganizationalUnit
            employeesCounter = cls.InstancesCounter()
            for ldapEmployee in ldapOrganizationalUnit.employees:
                try:
                    localEmployee = Employee.objects.get(user__username=ldapEmployee.username)
                    localEmployee.organizationalUnit = localOrganizationalUnit
                    localEmployee.save()
                    employeesCounter.synced += 1
                except Employee.DoesNotExist:
                    logger.warn(
                        u'Pracownik "%s" jest wymieniony w bazie LDAP jako członek jednostki organizacyjnej "%s", '
                        u'ale nie ma go w bazie LDAP wśród pracowników uczelni. '
                        u'Powiązanie jednostka-pracownik zostało zignorowane.',
                        ldapEmployee.username, ldapOrganizationalUnit.name
                    )
                    employeesCounter.nonSynced += 1

            logger.debug(
                u'Zaktualizowano zależności obiektu OrganizationalUnit: %s pracowników przypisano do cyklu, '
                u'%s pracowników wymienionych w jednostce nie odnaleziono w bazie.',
                employeesCounter.synced, employeesCounter.nonSynced
            )
        logger.info(
            u'Zaktualizowano dane %s jednostek organizacyjnych (w tym utworzono: %s)',
            organizationalUnitsCounter.synced, organizationalUnitsCounter.created
        )


    @classmethod
    def __syncOrganizations(cls, logger):
        u'''
        Synchronizuje bazę obiektów Organization z zewnętrzną bazą LDAP (modele LdapOrganization).
        '''
        organizationsCounter = cls.InstancesCounter()
        usersCounter = cls.InstancesCounter()

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
                logger.debug(u'W bazie odnaleziono użytkownika "%s" z powiązanym obiektem Organization.', ldapOrganization.username)
            except Organization.DoesNotExist:
                try:
                    localUser = User.objects.get(username=ldapOrganization.username)
                    logger.info(u'Użytkownik "%s" istnieje w bazie, jednak nie ma przypisanego obiektu Organization.', ldapOrganization.username)
                except User.DoesNotExist:
                    #TODO: być może last_login powinien być ustawiany na bardziej logiczną wartość, np. None
                    #      (w tej chwili niemożliwe, bo pole jest wymagane).
                    localUser = User(
                                     username=ldapOrganization.username,
                                     last_login=datetime(1970, 1, 1, tzinfo=pytz.utc),
                                     date_joined=timezone.now())
                    logger.info(u'Utworzono nowego użytkownika "%s".', localUser.username)
                    usersCounter.created += 1
                localOrganization = Organization()
                logger.info(u'Utworzono nowy obiekt Organization dla użytkownika "%s".', ldapOrganization.username)
                organizationsCounter.created += 1

            localUser.first_name = ldapOrganization.representantFirstName
            localUser.last_name = ldapOrganization.representantLastName
            localUser.email = ldapOrganization.representantEmail
            localUser.save()
            logger.debug(u'Zaktualizowano dane w obiekcie User: username="%s", pk="%s".', localUser.username, localUser.pk)
            usersCounter.synced += 1
            localOrganization.user = localUser
            localOrganization.name = ldapOrganization.name
            localOrganization.isLdapSynced = True
            localOrganization.save()
            permissions.registerOrganization(localOrganization)
            logger.debug(u'Zaktualizowano dane w obiekcie Organization: user.username="%s" pk="%s".', localOrganization.user.username, localOrganization.pk)
            organizationsCounter.synced += 1
        
        organizationsCounter.nonSynced = Organization.objects.filter(isLdapSynced=False).count()
        logger.info(
            u'Zsynchronizowano %s obiektów Organization (w tym utworzono: %s), pozostało niezsynchronizowanych: %s.',
            organizationsCounter.synced, organizationsCounter.created, organizationsCounter.nonSynced
        )
        logger.info(
            u'Zaktualizowano dane %s użytkowników (w tym utworzono: %s)',
            usersCounter.synced, usersCounter.created
        )


    @classmethod
    def __syncAuthorities(cls, logger):
        u'''
        Synchronizuje bazę obiektów Authority z zewnętrzną bazą LDAP (klasa pomocnicza LdapAuthorities).
        '''
        authoritiesCounter = cls.InstancesCounter()

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
        unknownRolesAuthorities = Authority.objects.exclude(role__in = [role.localName for role in authorityRoles])
        authoritiesCounter.deleted = unknownRolesAuthorities.count()
        if authoritiesCounter.deleted > 0:
            unknownRolesAuthorities.delete()
            logger.warn(u'Usunięto %s obiektów Authority mających role nieznane systemowi.', authoritiesCounter.deleted)

        #aktualizuj wszystkie lokalne obiekty Authority, które są odzwierciedlone w LDAPie
        for role in authorityRoles:
            ldapAuthority = None
            localAuthority = None
            try:
                ldapAuthority = LdapAuthorities.getAuthority(role.ldapName)
                localAuthority = Authority.objects.get(role=role.localName)
                logger.debug(u'W bazie odnaleziono obiekt Authority pasujący do właściwego obiektu w bazie LDAP (rola lokalna:"%s", rola LDAP: "%s".', role.localName, role.ldapName)
            except Authority.DoesNotExist:
                localAuthority = Authority(role=role.localName)
                logger.info(u'Utworzono nowy obiekt Authority dla roli "%s" (rola LDAP: "%s")', role.localName, role.ldapName)
                authoritiesCounter.created += 1
            except ldapModels_DoesNotExist:
                #Authority o tej roli nie istnieje w LDAPie
                logger.error(
                    u'W bazie LDAP nie odnaleziono obiektu Authority dla roli "%s" (poszukiwana rola LDAP: "%s")! '
                    u'Prawdopodobnie występuje niespójność pomiędzy bazą LDAP a konfiguracją serwisu. '
                    u'Obiekt Authority w bazie lokalnej (jeśli istnieje) nie zostanie usunięty, ale jego pole "occupant" zostanie wyczyszczone.',
                    role.localName, role.ldapName
                )
                try:
                    #usuń pracownika z lokalnej Authority, jeśli ona istnieje
                    localAuthority = Authority.objects.get(role=role.localName)
                    localAuthority.occupant = None
                    localAuthority.save()
                    logger.info(
                        u'Pole "ocupant" w obiekcie Authority dla roli "%s" (rola LDAP: "%s") zostało wyczyszczone.',
                        role.localName, role.ldapName
                    )
                    authoritiesCounter.synced += 1
                except Authority.DoesNotExist:
                    #jeśli nie istnieje - utwórz, ale z pustym polem [occupant]
                    localAuthority = Authority(role=role.localName)
                    localAuthority.save()
                    logger.info(
                        u'Dla roli "%s" (rola LDAP: "%s") utworzono nowy obiekt Authority z pustym polem "occupant".',
                        role.localName, role.ldapName
                    )
                    authoritiesCounter.created += 1
                    authoritiesCounter.synced += 1
                #pomiń resztę ciała pętli, bo wszystkie potrzebne zmiany dla tej roli zostały już poczynione
                # (nie można przypisać pracownika, a obiekt Authority już został zapisany)
                continue
                
            #przypisz pracownika pełniącego tę rolę
            localAuthority.occupant = Employee.objects.get(user__username=ldapAuthority.username)
            localAuthority.save()

            if localAuthority.role == Authority.DEAN:
                permissions.registerFacultyHead(localAuthority.occupant)
            elif localAuthority.role == Authority.VICE_DEAN_FOR_STUDENTS:
                permissions.registerFacultyHead(localAuthority.occupant)
            
            logger.debug(
                u'Obiektowi Authority o roli "%s" (rola LDAP: "%s") przypisano pracownika "%s".',
                role.localName, role.ldapName, localAuthority.occupant.user.username
            )
            authoritiesCounter.synced += 1

        logger.info(
            u'Zsynchronizowano %s obiektów Authority (w tym utworzono: %s), usunięto: %s.',
            authoritiesCounter.synced, authoritiesCounter.created, authoritiesCounter.deleted
        )