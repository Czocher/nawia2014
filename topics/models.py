# -*- coding: utf-8 -*-

u''' @package topics.models
Moduł gromadzący modele związane z tematami prac dyplomowych.
'''

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

    ### Identyfikator stanu tematu pracy dyplomowej.
    DRAFT = 'dr'
    ### Identyfikator stanu tematu pracy dyplomowej.
    VERIFICATION_READY = 'vr'
    ### Identyfikator stanu tematu pracy dyplomowej.
    DEPARTMENT_HEAD_VERIFIED = 'dv'
    ### Identyfikator stanu tematu pracy dyplomowej.
    FACULTY_HEAD_ACCEPTED = 'fa'
    ### Identyfikator stanu tematu pracy dyplomowej.
    REJECTED = 'rj'
    ### Identyfikator stanu tematu pracy dyplomowej.
    CANCELLED = 'cn'
    ### Identyfikator stanu tematu pracy dyplomowej.
    PUBLISHED = 'pb'
    ### Identyfikator stanu tematu pracy dyplomowej.
    ASSIGNED = 'as'

    ### Dostępne identyfikatory stanów tematów pracy dyplomowej wraz z tłumaczeniami.
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

    ### Temat pracy dyplomowej, dla którego zaszła zmiana stanu.
    thesisTopic = models.ForeignKey('ThesisTopic', related_name = 'statesHistory',
                                    verbose_name = 'ThesisTopicStateChange/thesis topic')

    ### Nowy stan tematu pracy dyplomowej.
    state = models.CharField(max_length = 2,
                             choices = THESIS_TOPIC_STATE_CHOICES,
                             default = DRAFT,
                             verbose_name = _('StateChange/state'))

    ### Automatycznie ustawia bieżący stan w przypisanym do siebie temacie pracy dyplomowej.
    def save(self, *args, **kwargs):
        # Przy dodawaniu zmiany stanu, ustawiamy dodawany stan jako aktualny do powiązanego tematu pracy.
        if self.id is None:
            self.thesisTopic.state = self
            self.thesisTopic.save()
        super(ThesisTopicStateChange, self).save(*args, **kwargs)


class Keyword(models.Model):
    u'''
    Słowo kluczowe opisujące dziedzinę, której dotyczy temat pracy.
    Propozycję struktury i implementację tego elementu systemu pozostawiamy naszym spadkobiercom.
    '''

    class Meta:
        verbose_name = _('Keyword')
        verbose_name_plural = _('Keywords')

    pass


class ThesisTopic(models.Model):
    u'''
    Temat pracy dyplomowej,
    '''

    class Meta:
        verbose_name = _('ThesisTopic')
        verbose_name_plural = _('ThesesTopics')

    ### Stan tematu pracy dyplomowej.
    state = models.ForeignKey(ThesisTopicStateChange, null = True, blank = True,
                              related_name = 'thesisTopicWithNewest',
                              verbose_name = _('ThesisTopic/state'))

    ### Autor tematu - co najmniej doktor lub firma zewnętrzna.
    ### Relacja z modelem 'User', ponieważ autor pracy może być klasy 'Employee' lub 'Organization'.
    author = models.ForeignKey(User, verbose_name =_('ThesisTopic/author'))
    title = models.CharField(max_length = 511,
                             verbose_name =_('ThesisTopic/topic'))
    description = models.TextField(verbose_name=_('ThesisTopic/description'))
    attachments = models.ManyToManyField(Attachment, null = True, blank = True,
                                         verbose_name = _('ThesisTopic/attachments'))
    ### Słowa kluczowe związane z problematyką poruszaną w pracy.
    keywords = models.ManyToManyField(Keyword, null = True, blank = True,
                                      verbose_name = _('ThesisTopic/keywords'))

    targetStudyCycles = models.ManyToManyField(StudyCycle, null = True, blank = True,
                                               related_name = 'thesisTopics',
                                               verbose_name = _('ThesisTopic/target study cycles'))

    ### Temat dedykowany?
    isDedicated = models.BooleanField(default = False)
    ### Osoby, którym dedykowany jest temat.
    dedicationTargets = models.ManyToManyField(Student, null = True, blank = True,
                                               verbose_name =_('ThesisTopic/dedication targets'))

    ### Praca zespołowa?
    coworkersLimit = models.PositiveSmallIntegerField(default = 1,
                                                      verbose_name =_('ThesisTopic/maximal number of coworkers'))

    def isTeamwork(self):
        u'''
        @returns Boolean
        '''
        return self.coworkersLimit > 1

    ### flaga określająca czy praca ma zostać opublikowana automatycznie po jej zatwierdzeniu przez wyższe szczeble
    isAutoPublished = models.BooleanField(default = True,
                                          verbose_name = _('ThesisTopic/published automatically'))

    def __unicode__(self):
        return self.title


class SubmissionCriterion(models.Model):
    u'''
    Tuple (authorship, criterion, value/response),
    eg. ('Authorship system, John Smith',
         'Object-oriented programming mark (floating point number)', '5').
    '''

    BOOLEAN_TYPE = 'b'
    INTEGER_TYPE = 'd'
    FLOAT_TYPE = 'f'
    CRITERION_TYPE_CHOICES = (
        (BOOLEAN_TYPE, _("Boolean type")),
        (INTEGER_TYPE, _("Integer type")),
        (FLOAT_TYPE, _("Float type")),
    )

    topic = models.ForeignKey(ThesisTopic, verbose_name=_("Topic"))
    __type = models.CharField(max_length=1, choices=CRITERION_TYPE_CHOICES,
                              verbose_name=_("Criterion type"))
    __value = models.CharField(max_length=15, db_column='value',
                               verbose_name=_("Value"))

    @property
    def value(self):
        u'''Returns the value in the correct type.'''
        if self.__type == SubmissionCriterion.BOOLEAN_TYPE:
            return bool(self.__value)
        elif self.__type == SubmissionCriterion.INTEGER_TYPE:
            return int(self.__value)
        elif self.__type == SubmissionCriterion.FLOAT_TYPE:
            return float(self.__value)
        else:
            return None

    @value.setter
    def value(self, value):
        self.__value = repr(value)

    def __unicode__(self):
        return '{} => {}'.format(self.criterion, self.value)

    class Meta:
        verbose_name = _("Submission Criterion")
        verbose_name_plural = _("Submission Criterions")
