# -*- coding: utf-8 -*-

u''' @package theses.models
Moduł gromadzący modele opisujące prace dyplomowe. 
'''

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from nawia.models import StateChange, Attachment
from authorships.models import Authorship
from faculty.models import Employee, Organization

class ThesisStateChange(StateChange):
    u'''
    Zmiana stanu pracy dyplomowej z uwzględnieniem czasu jej zajścia i osoby będącej jej źródłem.
    '''

    class Meta:
        verbose_name = _('ThesisStateChange')
        verbose_name_plural = _('ThesesStatesChanges')

    ### Identyfikator stanu pracy dyplomowej.
    IN_WORK = 'iw'
    ### Identyfikator stanu pracy dyplomowej.
    CANCELLED = 'cnl'
    ### Identyfikator stanu pracy dyplomowej.
    FAILED = 'fld'
    ### Identyfikator stanu pracy dyplomowej.
    FINISHED = 'fnd'
    ### Identyfikator stanu pracy dyplomowej.
    ANTIPLAGIARISM_TEST_PASSED = 'atp'
    ### Identyfikator stanu pracy dyplomowej.
    ANTIPLAGIARISM_TEST_FAILED = 'atf'
    ### Identyfikator stanu pracy dyplomowej.
    REVIEW_READY = 'rwr'
    ### Identyfikator stanu pracy dyplomowej.
    UNDER_REVIEW = 'urw'
    ### Identyfikator stanu pracy dyplomowej.
    REVIEW_PASSED = 'rwp'
    ### Identyfikator stanu pracy dyplomowej.
    DEFENCE_READY = 'dfr'
    ### Identyfikator stanu pracy dyplomowej.
    UNDER_DEFENCE = 'udf'
    ### Identyfikator stanu pracy dyplomowej.
    DEFENDED = 'dfd'
    ### Identyfikator stanu pracy dyplomowej.
    DEFENCE_FAILED = 'dff'

    ### Dostępne identyfikatory stanów pracy dyplomowej wraz z tłumaczeniami.
    THESIS_STATE_CHOICES = (
        (IN_WORK, _('ThesisStateChange/in work')),
        (CANCELLED, _('ThesisStateChange/cancelled')),
        (FAILED, _('ThesisStateChange/failed')),
        (FINISHED, _('ThesisStateChange/finished')),
        (ANTIPLAGIARISM_TEST_PASSED, _('ThesisStateChange/antiplagiarism test passed')),
        (ANTIPLAGIARISM_TEST_FAILED, _('ThesisStateChange/antiplagiarism test failed')),
        (REVIEW_READY, _('ThesisStateChange/ready to be reviewed')),
        (UNDER_REVIEW, _('ThesisStateChange/under review')),
        (REVIEW_PASSED, _('ThesisStateChange/reviews passed')),
        (DEFENCE_READY, _('ThesisStateChange/defence ready')),
        (UNDER_DEFENCE, _('ThesisStateChange/under defence')),
        (DEFENDED, _('ThesisStateChange/defended')),
        (DEFENCE_FAILED, _('ThesisStateChange/defence failed'))
    )
    ### Praca dyplomowa, dla której zaszła zmiana stanu.
    thesis = models.ForeignKey('Thesis', related_name = 'statesHistory',
                               verbose_name = 'ThesisStateChange/thesis')
    ### Nowy stan pracy dyplomowej.
    state = models.CharField(max_length = 3,
                             choices = THESIS_STATE_CHOICES,
                             default = IN_WORK,
                             verbose_name = _('StateChange/state'))

    ### Automatycznie ustawia bieżący stan w przypisanej do siebie pracy dyplomowej.
    def save(self, *args, **kwargs):
        # Przy dodawaniu zmiany stanu, ustawiamy dodawany stan jako aktualny do powiązanego tematu pracy.
        if self.id is None:
            self.thesis.state = self
            self.thesis.save()
        super(ThesisStateChange, self).save(*args, **kwargs)
   

class Thesis(models.Model):
    u'''
    Praca dyplomowa.

    Relacje odwrotne:
    Thesis.reviews : [Review]
    '''

    class Meta:
        verbose_name = _('Thesis')
        verbose_name_plural = _('Theses')

    state = models.ForeignKey(ThesisStateChange, null = True, blank = True,
                              related_name = 'thesisWithNewest',
                              verbose_name = _('ThesisTopic/state'))

    ### Zapis na pracę - zawiera dane typu temat, autor tematu, autor pracy.
    authorship = models.OneToOneField(Authorship, related_name = 'thesis',
                                      verbose_name = _('Thesis/autorship'))
    #TODO oddzielne pola 'document', 'schedule' typu Attachment
    attachments = models.ManyToManyField(Attachment, null = True, blank = True,
                                         verbose_name = ('Thesis/attachments'))

    ### Promotor.
    supervisor = models.ForeignKey(Employee, related_name = 'supervisedTheses',
                                   verbose_name = _('Thesis/supervisor'))
    ### Promotorzy pomocniczy.
    auxiliarySupervisors = models.ManyToManyField(Employee, null = True, blank = True,
                                                  related_name = 'auxiliarySupervisedTheses',
                                                  verbose_name = _('Thesis/auxiliary supervisors'))
    ### Doradcy - np. gdy autor tematu jest instutucją zewnętrzną, która nie ma prawa bycia promotorem.
    advisors = models.ManyToManyField(Organization, null = True, blank = True,
                                      related_name = 'advisedTheses',
                                      verbose_name = _('Thesis/advisors'))

    def student(self):
        u'''
        @returns faculty.models.Student
        '''
        return self.authorship.student

    def topic(self):
        u'''
        @returns topics.models.ThesisTopic
        '''
        return self.authorship.thesisTopic

    #def __unicode__(self):
    #    return u''#Praca dyplomowa - {}'.format(self.student)
        #return '%s, %s' % (self.topic.name, self.student)
