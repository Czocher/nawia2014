# -*- coding: utf-8 -*-
u'''Classes representing thesis authorship models.'''

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from faculty.models import Student
from topics.models import ThesisTopic


class Authorship(models.Model):

    u'''Model representing the relation between a student and his thesis topic.
    The student can enroll for a given topic, yet the supervisor must accept
    his enrollment first.'''

    PROPOSED = 'p'
    ACCEPTED = 'a'
    REJECTED = 'r'
    CANCELLED = 'c'
    AUTHORSHIP_STATE_CHOICES = (
        (PROPOSED, _("Proposed")),
        (ACCEPTED, _("Accepted")),
        (REJECTED, _("Rejected")),
        (CANCELLED, _("Cancelled")),
    )

    state = models.CharField(max_length=1,
                             choices=AUTHORSHIP_STATE_CHOICES,
                             default=PROPOSED,
                             verbose_name=_("State"))

    thesisTopic = models.ForeignKey(ThesisTopic, related_name='authorships',
                                    verbose_name=_("Thesis topic"))
    author = models.ForeignKey(Student, related_name='authorships',
                               verbose_name=_("Author"))
    comment = models.TextField(blank=True, verbose_name=_("Comments"))
    createdAt = models.DateTimeField(default=timezone.now, editable=False,
                                     null=True, blank=True,
                                     verbose_name=_("Created at"))
    updatedAt = models.DateTimeField(editable=False, null=True, blank=True,
                                     verbose_name=_("Updated at"))

    def save(self, *args, **kwargs):
        self.updatedAt = timezone.now()
        super(Authorship, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.get_state_display()

    class Meta:
        verbose_name = _("Authorship")
        verbose_name_plural = _("Authorships")
        ordering = ('updatedAt', )
