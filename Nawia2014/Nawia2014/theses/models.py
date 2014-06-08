# -*- coding: utf-8 -*-

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

    IN_WORK = 'iw'
    CANCELLED = 'cnl'
    FAILED = 'fld'
    FINISHED = 'fnd'
    ANTIPLAGIARISM_TEST_PASSED = 'atp'
    ANTIPLAGIARISM_TEST_FAILED = 'atf'
    REVIEW_READY = 'rwr'
    UNDER_REVIEW = 'urw'
    REVIEW_PASSED = 'rwp'
    DEFENCE_READY = 'dfr'
    UNDER_DEFENCE = 'udf'
    DEFENDED = 'dfd'
    DEFENCE_FAILED = 'dff'

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

    thesis = models.ForeignKey('Thesis', related_name = 'statesHistory',
                               verbose_name = 'ThesisStateChange/thesis')

    state = models.CharField(max_length = 3,
                             choices = THESIS_STATE_CHOICES,
                             default = IN_WORK,
                             verbose_name = _('StateChange/state'))

    def save(self, *args, **kwargs):
        # Przy dodawaniu zmiany stanu, ustawiamy dodawany stan jako aktualny do powiązanego tematu pracy.
        if self.id is None:
            self.thesis.state = self
            self.thesis.save()
        super(Authorship, self).save(*args, **kwargs)
   

class Thesis(models.Model):
    u'''
    Praca dyplomowa.
    '''

    class Meta:
        verbose_name = _('Thesis')
        verbose_name_plural = _('Theses')

    state = models.ForeignKey(ThesisStateChange, null = True, blank = True,
                              related_name = 'thesisWithNewest',
                              verbose_name = _('ThesisTopic/state'))

    # zapis na pracę zawiera dane typu temat, autor tematu, autor pracy
    authorship = models.OneToOneField(Authorship, related_name = 'thesis',
                                      verbose_name = _('Thesis/autorship'))
    #TODO oddzielne pola 'document', 'schedule' typu Attachment
    attachments = models.ManyToManyField(Attachment, null = True, blank = True,
                                         verbose_name = ('Thesis/attachments'))

    # promotor
    supervisor = models.ForeignKey(Employee, related_name = 'supervisedTheses',
                                   verbose_name = _('Thesis/supervisor'))
    # promotorzy pomocniczy
    auxiliarySupervisors = models.ManyToManyField(Employee, null = True, blank = True,
                                                  related_name = 'auxiliarySupervisedTheses',
                                                  verbose_name = _('Thesis/auxiliary supervisors'))
    # gdy autor tematu jest instutucją zewnętrzną, która nie ma prawa bycia promotorem
    advisor = models.ForeignKey(Organization, null = True, blank = True,
                                related_name = 'advisedTheses',                              
                                verbose_name = _('Thesis/advisor'))

    # relacja odwrotna
    # self.reviews : List<Review>
    
    # self.student : Student
    def student(self):
        return self.authorship.student

    # self.subject : ThesisTopic
    def topic(self):
        return self.authorship.thesisTopic

    def __unicode__(self):
        return '%s, %s' % (self.topic, self.student)
