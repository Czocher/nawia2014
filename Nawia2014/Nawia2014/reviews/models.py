# -*- coding: utf-8 -*-

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

    SUPERVISORS = 's'
    REVIEWERS = 'r'
    AUXILIARY_REVIEWERS = 'a'
    REVIEW_TYPE_CHOICES = (
        (SUPERVISORS, _('ReviewType/supervisor')),
        (REVIEWERS, _('ReviewType/reviewer')),
        (AUXILIARY_REVIEWERS, _('ReviewType/auxiliary reviewer')),
    )
    
    thesis = models.ForeignKey(Thesis, related_name = 'reviews')

    type = models.CharField(max_length = 1,
                                  choices = REVIEW_TYPE_CHOICES,
                                  verbose_name = _('Review/type'))
    author = models.ForeignKey(Employee,
                               verbose_name = _('Review/author'))
    comment = models.TextField(blank = True, verbose_name = _('Review/comment'))
    mark = models.FloatField(null = True, blank = True, verbose_name = _('Review/mark'))
    document = models.OneToOneField(Attachment, null = True, blank = True,
                                    related_name = 'reviews',
                                    verbose_name = _('Review/document'))

    #TODO: dodać pola 'deadline' (dla recenzenta) i 'uploadedAt'?

    attachments = models.ManyToManyField(Attachment, null = True, blank = True,
                                         verbose_name = _('Review/attachments'))

    def isDone(self):
        return self.document is not None

    def __unicode__(self):
        return u'%s (%s)' % (self.author, self.get_type_display())