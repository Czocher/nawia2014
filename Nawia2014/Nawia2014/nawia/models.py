# -*- coding: utf-8 -*-

import pytz
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

class ThesisSubject(models.Model):
    u'''
    Temat pracy dyplomowej
    '''
    statesHistory = models.ManyToManyField('ThesisSubjectStateChange', null = True, blank = True,
                                           verbose_name = _('history of states changes'))
    # self.state : ThesisSubjectStateChange

    title = models.CharField(max_length = 511, 
                             verbose_name =_('thesis title'))
    description = models.TextField(verbose_name=_('thesis description'))
    # słowa kluczowe związane z problematyką poruszaną w pracy
    keywords = models.ManyToManyField('Keyword', null = True, blank = True, 
                                      verbose_name =_('keywords'))
    
    # TODO obsługa prac dedykowanych
    # isDedicated = models.BooleanField(default = false)
    # dedicationTargets = models.ManyToManyField('Student')
    
    # maksymalna liczba osób w zespole, jeśli jest to praca zespołowa
    teamMembersLimit = models.PositiveSmallIntegerField(default = 1, 
                                                        verbose_name =_('number of team members'))
    # self.isTeamWork = teamMembersLimit > 1 ? True : False

    # autor tematu - co najmniej doktor lub firma zewnętrzna
    # relacja z modelem 'User', ponieważ autor pracy może być klasy 'Employee' lub 'Organization'
    author = models.ForeignKey(User, 
                               verbose_name =_('author of thesis subject'))

    attachments = models.ManyToManyField('Attachment', null = True, blank = True, 
                                         verbose_name =_('attachments'))

    # pytania, na które musi odpowiedzieć osoba zgłaszająca chęć pisania pracy na dany temat
    # na podstawie wartości kryteriów ustalana jest kolejność studentów na liście zainteresowanych
    criteria = models.ManyToManyField('SubmissionCriterion', null = True, blank = True, 
                                        verbose_name =_('questions for the student who apply to write a given thesis'))

    # flaga określająca czy praca ma zostać opublikowana automatycznie po jej zatwierdzeniu przez wyższe szczeble
    isAutoPublished = models.BooleanField(default = True, 
                                            verbose_name = _('is published automatically'))

    def __getattr__(self, name):
        if name == 'state':
            return self.statesHistory.latest()
        elif name == 'isTeamWork':
            return self.teamMembersLimit > 1
        else:
            raise AttributeError(name)

    def __unicode__(self):
        return '"%s" - %s' % (self.title, self.author)

    class Meta:
        verbose_name = _('subject of thesis')
        verbose_name_plural = _('subjects of theses')

class ThesisSubjectStateChange(models.Model):
    u'''
    Zmiana stanu tematu pracy z uwzględnieniem czasu jej zajścia i osoby będącej jej źródłem.
    '''
    DRAFT = 'dr'
    VERIFICATION_READY = 'vr'
    DEPARTMENT_HEAD_VERIFIED = 'dv'
    FACULTY_HEAD_VERIFIED = 'fv'
    REJECTED = 'rj'
    CANCELLED = 'cn'
    PUBLISHED = 'pb'
    ASSIGNED = 'as'
    THESIS_SUBJECT_STATE_CHOICES = (
        (DRAFT, 'draft'),
        (VERIFICATION_READY, 'ready to verify'),
        (DEPARTMENT_HEAD_VERIFIED, 'verified by the Head of Department'),
        (FACULTY_HEAD_VERIFIED, 'verified by the Head of Faculty'),
        (REJECTED, 'rejected'),
        (CANCELLED, 'cancelled'),
        (PUBLISHED, 'published'),
        (ASSIGNED, 'assigned'),   
    )
    state = models.CharField(max_length = 2,
                             choices = THESIS_SUBJECT_STATE_CHOICES,
                             default = DRAFT,
                             verbose_name = _('actual thesis subject state'))

    # osobami mogącymi powodować zmianę stanu są kierownicy katedr, dziekani/prodziekani lub autor pracy
    # relacja z modelem 'User', ponieważ autor pracy może być klasy 'Employee' lub 'Organization'
    initiator = models.ForeignKey(User, null = True, blank = True, 
                                    verbose_name = _('person responsible for changing thesis subject state'))
    # dodatkowa informacja nt. zmiany stanu, uzasadnienie decyzji np. odrzucenia tematu
    comment = models.TextField(blank = True, 
                               verbose_name = _('note about thesis subject state'))

    occuredAt = models.DateTimeField(default = timezone.now, editable = False, null = True, blank = True, 
                                     verbose_name = _('happend'))

    def __unicode__(self):
        return '%s (%s), %s' % (self.get_state_display(), self.occuredAt, self.initiator)

    class Meta:
        get_latest_by = "occuredAt"
        verbose_name = _('state change of thesis subject')
        verbose_name_plural = _('states changes of thesis subject')

class Thesis(models.Model):
    u'''
    Praca dyplomowa
    '''
    IN_WORK = 'in work'
    REVIEW_READY = 'ready to be reviewed'
    IN_REVIEW = 'in review'
    REVIEWED = 'reviewed'
    CANCELLED = 'cancelled'
    UNKNOWN_REVIEWS_PROGRESS = 'unknown reviews progress'

    # zapis na pracę zawiera dane typu temat, autor tematu, autor pracy
    authorship = models.OneToOneField('Authorship', 
                                      verbose_name = _('informations about thesis'))
    isDone = models.BooleanField(default = False, 
                                 verbose_name = _('inform if thesis is done'))
    attachments = models.ManyToManyField('Attachment', null = True, blank = True, 
                                         verbose_name = ('attachments'))

    # promotor
    supervisor = models.ForeignKey('Employee',
                                   related_name = 'supervisedThesis',
                                   verbose_name = _('supervisor'))
    # promotorzy pomocniczy
    auxiliarySupervisors = models.ManyToManyField('Employee',
                                                  related_name = 'auxiliarySupervisedThesis',
                                                  null = True, blank = True,
                                                  verbose_name = _('auxiliary supervisors'))
    # gdy autor tematu jest instutucją zewnętrzną, która nie ma prawa bycia promotorem
    advisor = models.ForeignKey('Organization',
                                related_name = 'advisedThesis',
                                null = True, blank = True,
                                verbose_name = _('advisor'))

    reviews = models.ManyToManyField('Review', null = True, blank = True,
                                     verbose_name = _('thesis reviews'))
    
    # self.state
    # TODO zastanowić się nad stanami recenzji
    def __getState(self):
        if self.authorship.state == Authorship.CANCELLED:
            return Thesis.CANCELLED
        else:
            if not self.isDone:
                return Thesis.IN_WORK
            else:
                if len(self.reviews) == 0:
                    return Thesis.REVIEW_READY
                else:
                    reviewed = True
                    for review in self.reviews:
                        if not review.isDone:
                            reviewed = False
                    if reviewed:
                        return self.REVIEWED
                    else:
                        return self.IN_REVIEW
                

    # self.student : Student
    def __getStudent(self):
        return self.authorship.student

    # self.subject : ThesisSubject
    def __getSubject(self):
        return self.authorship.thesisSubject

    def __getattr__(self, name):
        if name == 'student':
            return self.__getStudent()
        elif name == 'subject':
            return self.__getSubject()
        elif name == 'state':
            return self.__getState()
        else:
            raise AttributeError(name)

    def __unicode__(self):
        return '"%s", %s, %s' % (self.subject, self.student, self.supervisor)
    
    class Meta:
        verbose_name = _('thesis')
        verbose_name_plural = _('theses')
        
class Authorship(models.Model):
    u'''
    Powiązanie studenta z tematem pracy, na który się początkowo zapisuje, a następnie (po zaakceptowaniu przez promotora) realizuje.
    '''
    PROPOSED = 'p'
    ACCEPTED = 'a'
    REJECTED = 'r'
    CANCELLED = 'c'
    AUTHORSHIP_STATE_CHOICES = (
        (PROPOSED, 'proposed'),
        (ACCEPTED, 'accepted'),
        (REJECTED, 'rejected'),
        (CANCELLED, 'cancelled'),
    )
    state = models.CharField(max_length = 1,
                             choices = AUTHORSHIP_STATE_CHOICES,
                             default = PROPOSED,
                             verbose_name = _('authorship state'))

    thesisSubject = models.ForeignKey('ThesisSubject',
                                      verbose_name = _('subject of thesis'))
    # dodatkowe informacje przekazywane autorowi tematu,
    # np. uzasadnienie chęci pisania pracy na dany temat lub przypomnienie o odbytej rozmowie
    comment = models.TextField(blank = True,
                               verbose_name = _('informations from student to thesis subject author'))
    
    student = models.ForeignKey('Student',
                                verbose_name = _('student'))

    createdAt = models.DateTimeField(editable = False, null = True, blank = True,
                                     verbose_name = _('date of authorship proposal'))
    updatedAt = models.DateTimeField(editable = False, null = True, blank = True,
                                     verbose_name = _('date of last modification'))

    def save(self, *args, **kwargs):
        if self.id != None:
            self.updatedAt = timezone.now()
        else:
            self.createdAt = timezone.now()
        super(Authorship, self).save(*args, **kwargs)

    def __unicode__(self):
        return '"%s", %s (%s)' % (self.subject, self.student, self.get_state_display())
        
    class Meta:
        verbose_name = _('authorship')
        verbose_name_plural = _('authorships')

class SubmissionCriterion(models.Model):
    u'''
    Rodzaj kryterium/pytania kierowanego przez autora tematu do zgłaszających się studentów.
    '''
    BOOLEAN = 'b'
    INTEGER = 'd'
    FLOAT = 'f'
    CRITERION_TYPE_CHOICES = (
        (BOOLEAN, 'boolean'),
        (INTEGER, 'integer'),
        (FLOAT, 'float'),
    )
    type = models.CharField(max_length = 1,
                            choices = CRITERION_TYPE_CHOICES,
                            verbose_name = _('type of the criterion'))
    label = models.CharField(max_length = 255,
                             verbose_name = _('content of the criterion'))

    def __unicode__(self):
        return '%s (%s)' % (self.label, self.get_type_display())
    
    class Meta:
        verbose_name = _('submission criterion')
        verbose_name_plural = _('submission criteria')
        
class SubmissionCriterionValue(models.Model):
    u'''
    Para (kryterium, wartość/odpowiedź), np. (Ocena z programowania obiektowego (float), '3.5').
    '''
    criterion = models.ForeignKey('SubmissionCriterion',
                                  verbose_name = _('criterion'))
    __value = models.CharField(max_length = 15, db_column = 'value',
                               verbose_name = _('value of criterion'))

    # self.value getter
    def __getValue(self):
        type = self.criterion.type
        if type == SubmissionCriterion.BOOLEAN:
            return bool(self.__value)
        elif type == SubmissionCriterion.INTEGER:
            return int(self.__value)
        elif type == SubmissionCriterion.FLOAT:
            return float(self.__value)
        else:
            return None
        # alternatywnie
        # return eval(self.__value)

    # self.value setter
    def __setValue(self, value):
        self.__value = repr(value)

    def __getattr__(self, name):
        if name == 'value':
            return self.__getValue()
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name == 'value':
            self.__setValue(value)
        else:
            raise AttributeError(name)

    def __unicode__(self):
        return '%s => %s' % (self.criterion, self.value)
    
    class Meta:
        verbose_name = _('submission criterion value')
        verbose_name_plural = _('submission criteria values')
        
class Review(models.Model):
    SUPERVISOR = 's'
    REVIEWER = 'r'
    AUXILIARY_REVIEWER = 'a'
    REVIEW_AUTHOR_TYPE_CHOICES = (
        (SUPERVISOR, 'supervisor'),
        (REVIEWER, 'reviewer'),
        (AUXILIARY_REVIEWER, 'auxiliary reviewer'),
    )
    authorType = models.CharField(max_length = 1,
                             choices = REVIEW_AUTHOR_TYPE_CHOICES,
                             verbose_name = _('review author type'))
    author = models.ForeignKey('Employee',
                                verbose_name = _('review author'))

    comment = models.TextField(blank = True,
                               verbose_name = _("reviewer's comment"))
    mark = models.FloatField(null = True, blank = True,
                             verbose_name = _('mark')) # dodać walidację
    isDone = models.BooleanField(default = False,
                                 verbose_name = _('information about adding review'))

    attachments = models.ManyToManyField('Attachment', null = True, blank = True,
                                         verbose_name = _('attachments'))

    def __unicode__(self):
        return '%s (%s) => %s' % (self.author, self.get_authorType_display(), self.mark)
    
    class Meta:
        verbose_name = _('review')
        verbose_name_plural = _('reviews')
        
class Attachment(models.Model):
    class Meta:
        verbose_name = _('attachment')
        verbose_name_plural = _('attachments')

class Keyword(models.Model):
    class Meta:
        verbose_name = _('keyword')
        verbose_name_plural = _('keywords')

class StudyCycle(models.Model):
    u'''
    Cykl kształcenia (np. informatyka, inżynierskie, stacjonarne, 2011Z-2014Z)
    '''
    ldapId = models.CharField(max_length = 255, unique = True,
                              verbose_name = _('LDAP ID'))
    name = models.CharField(max_length = 255,
                            verbose_name = _('study cycle name'))

    submissionsOpenAt = models.DateField(default=None, null=True, blank=True,
                                         verbose_name = _('start of submissions'))
    submissionsCloseAt = models.DateField(default=None, null=True, blank=True,
                                          verbose_name = _('end of submissions'))
    isLdapSynced = models.BooleanField(default=False,
                                       verbose_name = _('is synced with LDAP'))
        
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('study cycle')
        verbose_name_plural = _('study cycles')

class UserBasedModel(models.Model):
    user = models.OneToOneField(User, verbose_name = _('user'))
    isLdapSynced = models.BooleanField(default=False, editable=False,
                                       verbose_name = _('is synced with LDAP'))

    class Meta:
        abstract = True
        verbose_name = _('user based model')
        verbose_name_plural = _('users based models')
        
class Student(UserBasedModel):
    # jeden student może realizować wiele cykli kształcenia
    studyCycles = models.ManyToManyField('StudyCycle', null = True, blank = True,
                                         verbose_name = _('study cycle')) # tymczasowo

    def __unicode__(self):
        return unicode(self.user)
    
    class Meta:
        verbose_name = _('student')
        verbose_name_plural = _('students')

class Employee(UserBasedModel):
    u'''
    Pracownik uczelni
    '''
    # tytuł naukowy
    title = models.CharField(max_length = 255, blank = True,
                             verbose_name = _('academic title'))
    # stanowisko pracy (asystent, adiunkt, itp.)
    position = models.CharField(max_length = 255, blank = True,
                                verbose_name = _('worksite'))

    # jednostka organizacyjna (katedra, zakład, itp.), do której należy dany pracownik
    organizationalUnit = models.ForeignKey('OrganizationalUnit', null = True, blank = True,
                                            verbose_name = _('organizational unit'))

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
        return '%s %s' % (self.title, self.user)
        
    class Meta:
        verbose_name = _('employee')
        verbose_name_plural = _('employess')

class Organization(UserBasedModel):
    u'''
    Organizacja zewnętrzna (firma, stowarzyszenie, urząd, itp.)
    '''
    name = models.CharField(max_length = 255,
                            verbose_name = _('organization name'))

    def __unicode__(self):
        return '%s, %s' % (self.name, self.user)
    
    class Meta:
        verbose_name = _('organization')
        verbose_name_plural = _('organizations')

class OrganizationalUnit(models.Model):
    u'''
    Jednostka organizacyjna (katedra, dziekanat, itp.)
    '''
    ldapId = models.CharField(max_length = 31, unique = True,
                              verbose_name = _('LDAP ID'))
    name = models.CharField(max_length = 255,
                            verbose_name = _('organizational unit name'))
    head = models.ForeignKey(Employee, null = True, blank = True,
                             verbose_name = _('head of organizational unit')) # 'null = True' prawdopodonie tymczasowo

    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name = _('organizational unit')
        verbose_name_plural = _('organizational units')

class Authority(models.Model):
    u'''
    Władze wydziału
    '''
    DEAN = 'd'
    VICE_DEAN_FOR_PROMOTION = 'pr'
    VICE_DEAN_FOR_RESEARCH = 'sc'
    VICE_DEAN_FOR_STUDENTS = 'st'
    AUTHORITY_ROLES_CHOICES = (
        (DEAN, 'Dean'),
        (VICE_DEAN_FOR_PROMOTION, 'Vice-Dean for Promotion and Cooperation'),
        (VICE_DEAN_FOR_RESEARCH, 'Vice-Dean for Research'),
        (VICE_DEAN_FOR_STUDENTS, 'Vice-Dean for Teaching and Students'),
    )
    role = models.CharField(max_length = 2,
                            choices = AUTHORITY_ROLES_CHOICES,
                            verbose_name = _('authority role'))
    occupant = models.ForeignKey('Employee', null = True, blank = True,
                                 verbose_name = _('person occupying the worksite'))

    def __unicode__(self):
        return '%s => %s' % (self.get_role_display(), self.occupant)
    
    class Meta:
        verbose_name = _('authority')
        verbose_name_plural = _('authorities')

