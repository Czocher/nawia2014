# -*- coding: utf-8 -*-

u''' @package authorships.models
Moduł gromadzący wszystkie modele opisujące dane związane z autorstwem prac dyplomowych.
'''

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

    Relacje odwrotne:
    Authorship.criteriaValues : [SubmissionCriterionValue]
    '''
    
    class Meta:
        verbose_name = _('Authorship')
        verbose_name_plural = _('Authorships')
        ordering = ('updatedAt', )

    ### Identyfikator stanu autorstwa pracy: zaproponowane.
    PROPOSED = 'p'
    ### Identyfikator stanu autorstwa pracy: zaakceptowane.
    ACCEPTED = 'a'
    ### Identyfikator stanu autorstwa pracy: odrzucone.
    REJECTED = 'r'
    ### Identyfikator stanu autorstwa pracy: anulowane.
    CANCELLED = 'c'
    ### Dostępne identyfikatory stanów autorstwa pracy wraz z tłumaczeniami.
    AUTHORSHIP_STATE_CHOICES = (
        (PROPOSED, _('AuthorshipState/proposed')),
        (ACCEPTED, _('AuthorshipState/accepted')),
        (REJECTED, _('AuthorshipState/rejected')),
        (CANCELLED, _('AuthorshipState/cancelled')),
    )
    ### Stan autorstwa pracy.
    state = models.CharField(max_length = 1,
                             choices = AUTHORSHIP_STATE_CHOICES,
                             default = PROPOSED,
                             verbose_name = _('Authorship/authorship state'))

    ### Temat pracy.
    thesisTopic = models.ForeignKey(ThesisTopic, related_name = 'authorships',
                                    verbose_name = _('Authorship/thesis topic'))
    ### Student-autor.
    student = models.ForeignKey(Student, related_name = 'authorships',
                                verbose_name = _('Authorship/student'))
    ### dodatkowe informacje przekazywane autorowi tematu,
    ### np. uzasadnienie chęci pisania pracy na dany temat lub przypomnienie o odbytej rozmowie
    comment = models.TextField(blank = True, verbose_name = _('Authorship/comment'))
    
    createdAt = models.DateTimeField(default = timezone.now, editable = False, null = True, blank = True,
                                     verbose_name = _('Authorship/date of proposal'))
    updatedAt = models.DateTimeField(editable = False, null = True, blank = True,
                                     verbose_name = _('Authorship/date of last modification'))

    
    def save(self, *args, **kwargs):
        u'''
        Automatycznie wypełnia Authorship.updatedAt.
        '''
        self.updatedAt = timezone.now()
        super(Authorship, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.get_state_display()

        
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

    def __getValue(self):
        u'''
        Getter self.value. Odwoływać się przez SubmissionCriterionValue.value.
        '''
        type = self.criterion.type
        if type == SubmissionCriterion.BOOLEAN:
            return bool(self.__value)
        elif type == SubmissionCriterion.INTEGER:
            return int(self.__value)
        elif type == SubmissionCriterion.FLOAT:
            return float(self.__value)
        else:
            return None
        # alternatywnie:
        # return ast.literal_eval(self.__value)

    def __setValue(self, value):
        u'''
        Setter self.value. Odwoływać się przez SubmissionCriterionValue.value.
        '''
        self.__value = repr(value)

    def __getattr__(self, name):
        u'''
        Zapewnia przekierowanie odczytów atrybutu SubmissionCriterionValue.value
        na wywołania metody SubmissionCriterionValue.__getValue().
        '''
        if name == 'value':
            return self.__getValue()
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        u'''
        Zapewnia przekierowanie zapisów atrybutu SubmissionCriterionValue.value
        na wywołania metody SubmissionCriterionValue.__setValue().
        '''
        if name == 'value':
            self.__setValue(value)
        else:
            raise AttributeError(name)

    def __unicode__(self):
        return '%s => %s' % (self.criterion, self.value)
