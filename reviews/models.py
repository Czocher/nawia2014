# -*- coding: utf-8 -*-

u''' @package reviews.models
Moduł gromadzący modele związane z recenzjami prac dyplomowych.
'''

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from nawia.models import Attachment
from faculty.models import Employee
from theses.models import Thesis

class Review(models.Model):
    u'''
    Recenzja pracy dyplomowej.
    '''

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

    ### Identyfikator typu recenzji.
    SUPERVISORS = 's'
    ### Identyfikator typu recenzji.
    REVIEWERS = 'r'
    ### Identyfikator typu recenzji.
    AUXILIARY_REVIEWERS = 'a'

    ### Dostępne identyfikatory typów recenzji wraz z tłumaczeniami.
    REVIEW_TYPE_CHOICES = (
        (SUPERVISORS, _('ReviewType/supervisor')),
        (REVIEWERS, _('ReviewType/reviewer')),
        (AUXILIARY_REVIEWERS, _('ReviewType/auxiliary reviewer')),
    )
    
    thesis = models.ForeignKey(Thesis, related_name = 'reviews')

    ### Typ recenzji.
    type = models.CharField(max_length = 1,
                                  choices = REVIEW_TYPE_CHOICES,
                                  verbose_name = _('Review/type'))
    ## Autor.
    author = models.ForeignKey(Employee,
                               verbose_name = _('Review/author'))
    ### Komentarz.
    comment = models.TextField(blank = True, verbose_name = _('Review/comment'))
    ### Ocena.
    mark = models.FloatField(null = True, blank = True, verbose_name = _('Review/mark'))
    ### Dokumant zawierający treść recenzji.
    document = models.OneToOneField(Attachment, null = True, blank = True,
                                    related_name = 'reviews',
                                    verbose_name = _('Review/document'))

    #TODO: dodać pola 'deadline' (dla recenzenta) i 'uploadedAt'?

    ### Załączniki.
    attachments = models.ManyToManyField(Attachment, null = True, blank = True,
                                         verbose_name = _('Review/attachments'))

    def isDone(self):
        u'''
        @returns Boolean
        '''
        return self.document is not None

    def __unicode__(self):
        return u'%s (%s)' % (self.author, self.get_type_display())
