# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from nawia.models import StateChange, Attachment
from faculty.models import StudyCycle, Student

class ThesisTopicStateChange(StateChange):
    u'''
    Zmiana stanu tematu pracy z uwzględnieniem czasu jej zajścia i osoby będącej jej źródłem.
    '''

    class Meta:
        verbose_name = _('ThesisTopicStateChange')
        verbose_name_plural = _('ThesesTopicsStatesChanges')

    DRAFT = 'dr'
    VERIFICATION_READY = 'vr'
    DEPARTMENT_HEAD_VERIFIED = 'dv'
    FACULTY_HEAD_ACCEPTED = 'fa'
    REJECTED = 'rj'
    CANCELLED = 'cn'
    PUBLISHED = 'pb'
    ASSIGNED = 'as'

    THESIS_TOPIC_STATE_CHOICES = (
        (DRAFT, _('ThesisTopicState/draft')),
        (VERIFICATION_READY, _('ThesisTopicState/ready to verify')),
        (DEPARTMENT_HEAD_VERIFIED, _('ThesisTopicState/verified by the Head of Department')),
        (FACULTY_HEAD_ACCEPTED, _('ThesisTopicState/accepted by the Head of Faculty')),
        (REJECTED, _('ThesisTopicState/rejected')),
        (CANCELLED, _('ThesisTopicState/cancelled')),
        (PUBLISHED, _('ThesisTopicState/published')),
        (ASSIGNED, _('ThesisTopicState/assigned')),   
    )

    thesisTopic = models.ForeignKey('ThesisTopic', related_name = 'statesHistory',
                                    verbose_name = 'ThesisTopicStateChange/thesis topic')

    state = models.CharField(max_length = 2,
                             choices = THESIS_TOPIC_STATE_CHOICES,
                             default = DRAFT,
                             verbose_name = _('StateChange/state'))

    def save(self, *args, **kwargs):
        # Przy dodawaniu zmiany stanu, ustawiamy dodawany stan jako aktualny do powiązanego tematu pracy.
        if self.id is None:
            self.thesisTopic.state = self
            self.thesisTopic.save()
        super(Authorship, self).save(*args, **kwargs)
        

class Keyword(models.Model):
    u'''
    Słowo kluczowe opisujące dziedzinę, której dotyczy temat pracy.
    Propozycję struktury i implementację tego elementu systemu pozostawiamy naszym spadkobiercom.
    '''

    class Meta:
        verbose_name = _('Keyword')
        verbose_name_plural = _('Keywords')

    pass

class SubmissionCriterion(models.Model):
    u'''
    Rodzaj kryterium/pytania kierowanego przez autora tematu do zgłaszających się studentów.
    '''

    class Meta:
        verbose_name = _('SubmissionCriterion')
        verbose_name_plural = _('SubmissionsCriteria')

    BOOLEAN = 'b'
    INTEGER = 'd'
    FLOAT = 'f'
    CRITERION_TYPE_CHOICES = (
        (BOOLEAN, 'CriterionType/boolean'),
        (INTEGER, 'CriterionType/integer'),
        (FLOAT, 'CriterionType/float'),
    )
    type = models.CharField(max_length = 1,
                            choices = CRITERION_TYPE_CHOICES,
                            verbose_name = _('SubmissionCriterion/type'))
    label = models.CharField(max_length = 255,
                             verbose_name = _('SubmissionCriterion/label'))

    def __unicode__(self):
        return '%s (%s)' % (self.label, self.get_type_display())


class ThesisTopic(models.Model):
    u'''
    Temat pracy dyplomowej
    '''

    class Meta:
        verbose_name = _('ThesisTopic')
        verbose_name_plural = _('ThesesTopics')

    state = models.ForeignKey(ThesisTopicStateChange, null = True, blank = True,
                              related_name = 'thesisTopicWithNewest',
                              verbose_name = _('ThesisTopic/state'))

    # autor tematu - co najmniej doktor lub firma zewnętrzna
    # relacja z modelem 'User', ponieważ autor pracy może być klasy 'Employee' lub 'Organization'
    author = models.ForeignKey(User, verbose_name =_('ThesisTopic/author'))
    title = models.CharField(max_length = 511, 
                             verbose_name =_('ThesisTopic/topic'))
    description = models.TextField(verbose_name=_('ThesisTopic/description'))
    attachments = models.ManyToManyField(Attachment, null = True, blank = True, 
                                         verbose_name = _('ThesisTopic/attachments'))
    # słowa kluczowe związane z problematyką poruszaną w pracy
    keywords = models.ManyToManyField(Keyword, null = True, blank = True, 
                                      verbose_name = _('ThesisTopic/keywords'))

    targetStudyCycles = models.ManyToManyField(StudyCycle, null = True, blank = True,
                                               related_name = 'thesisTopics',
                                               verbose_name = _('ThesisTopic/target study cycles'))
    
    # temat dedykowany
    isDedicated = models.BooleanField(default = False)
    dedicationTargets = models.ManyToManyField(Student, null = True, blank = True,
                                               verbose_name =_('ThesisTopic/dedication targets'))
    
    # praca zespołowa
    coworkersLimit = models.PositiveSmallIntegerField(default = 1,
                                                      verbose_name =_('ThesisTopic/maximal number of coworkers'))

    def isTeamwork(self):  # self.isTeamWork : bool
        return self.coworkersLimit > 1

    # pytania, na które musi odpowiedzieć osoba zgłaszająca chęć pisania pracy na dany temat
    # na podstawie wartości kryteriów ustalana jest kolejność studentów na liście zainteresowanych
    criteria = models.ManyToManyField(SubmissionCriterion, null = True, blank = True, 
                                      verbose_name =_('ThesisTopic/sumbission criteria'))

    # flaga określająca czy praca ma zostać opublikowana automatycznie po jej zatwierdzeniu przez wyższe szczeble
    isAutoPublished = models.BooleanField(default = True, 
                                          verbose_name = _('ThesisTopic/published automatically'))

    def __unicode__(self):
        return self.title
