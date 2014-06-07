# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from faculty.models import Student
from topics.models import ThesisTopic, SubmissionCriterion

class Authorship(models.Model):
    u'''
    Powiązanie studenta z tematem pracy, na który się początkowo zapisuje,
    a następnie (po zaakceptowaniu przez promotora) realizuje.
    '''
    
    class Meta:
        verbose_name = _('Authorship')
        verbose_name_plural = _('Authorships')
        ordering = ('updatedAt', )

    PROPOSED = 'p'
    ACCEPTED = 'a'
    REJECTED = 'r'
    CANCELLED = 'c'
    AUTHORSHIP_STATE_CHOICES = (
        (PROPOSED, _('AuthorshipState/proposed')),
        (ACCEPTED, _('AuthorshipState/accepted')),
        (REJECTED, _('AuthorshipState/rejected')),
        (CANCELLED, _('AuthorshipState/cancelled')),
    )
    state = models.CharField(max_length = 1,
                             choices = AUTHORSHIP_STATE_CHOICES,
                             default = PROPOSED,
                             verbose_name = _('Authorship/authorship state'))

    thesisTopic = models.ForeignKey(ThesisTopic, related_name = 'authorships',
                                    verbose_name = _('Authorship/thesis topic'))
    student = models.ForeignKey(Student, related_name = 'authorships',
                                verbose_name = _('Authorship/student'))
    # dodatkowe informacje przekazywane autorowi tematu,
    # np. uzasadnienie chęci pisania pracy na dany temat lub przypomnienie o odbytej rozmowie
    comment = models.TextField(blank = True, verbose_name = _('Authorship/comment'))
    
    createdAt = models.DateTimeField(default = timezone.now, editable = False, null = True, blank = True,
                                     verbose_name = _('Authorship/date of proposal'))
    updatedAt = models.DateTimeField(editable = False, null = True, blank = True,
                                     verbose_name = _('Authorship/date of last modification'))

    # relacja odwrotna
    # self.criteriaValues : List<SubmissionCriterionValue>

    def save(self, *args, **kwargs):
        self.updatedAt = timezone.now()
        super(Authorship, self).save(*args, **kwargs)

    def __unicode__(self):
        return '"%s", %s (%s)' % (self.subject, self.student, self.get_state_display())

        
class SubmissionCriterionValue(models.Model):
    u'''
    Krotka (autorstwo, kryterium, wartość/odpowiedź),
    np. ('Internetowy system wspomagający proces dyplomowania na uczelni, Jan Kowalski', 'Ocena z programowania obiektowego (liczba zmiennoprzecinkowa)', '5').
    '''

    class Meta:
        verbose_name = _('SubmissionCriterionValue')
        verbose_name_plural = _('SubmissionsCriteriaValues')

    authorship = models.ForeignKey(Authorship, related_name = 'criteriaValues',
                                   verbose_name = _('SubmissionCriterionValue/authorship'))
    criterion = models.ForeignKey(SubmissionCriterion, related_name = 'values',
                                  verbose_name = _('SubmissionCriterionValue/criterion'))
    __value = models.CharField(max_length = 15, db_column = 'value',
                               verbose_name = _('SubmissionCriterionValue/value'))

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