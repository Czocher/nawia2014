# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from nawia.models import Attachment
from faculty.models import Employee

class Review(models.Model):
    u'''
    Recenzja pracy dyplomowej.
    '''

    class Meta:
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')

    SUPERVISOR = 's'
    REVIEWER = 'r'
    AUXILIARY_REVIEWER = 'a'
    REVIEW_AUTHOR_TYPE_CHOICES = (
        (SUPERVISOR, 'Review/supervisor'),
        (REVIEWER, 'Review/reviewer'),
        (AUXILIARY_REVIEWER, 'Review/auxiliary reviewer'),
    )

    authorType = models.CharField(max_length = 1,
                                  choices = REVIEW_AUTHOR_TYPE_CHOICES,
                                  verbose_name = _('Review/author type'))
    author = models.ForeignKey(Employee,
                               verbose_name = _('Review/author'))
    comment = models.TextField(blank = True, verbose_name = _('Review/comment'))
    mark = models.FloatField(null = True, blank = True, verbose_name = _('Review/mark'))
    document = models.OneToOneField(Attachment, null = True, blank = True,
                                    related_name = 'reviews',
                                    verbose_name = 'Review/document')

    #TODO: dodać pola 'deadline' (dla recenzenta) i 'uploadedAt'?

    attachments = models.ManyToManyField(Attachment, null = True, blank = True,
                                         verbose_name = _('Review/attachments'))

    def isDone(self):
        return self.document is not None

    def __unicode__(self):
        return '%s (%s)' % (self.author, self.get_authorType_display())