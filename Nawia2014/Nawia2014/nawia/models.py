# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

class StateChange(models.Model):
    class Meta:
        ordering = '-occuredAt'
        get_latest_by = 'occuredAt'
        abstract = True

    # Osobami mogącymi powodować zmianę stanu są pracownicy, studenci, bądź organizacje zewnętrzne.
    # Relacja z modelem 'User', ponieważ inicjator może być obiektem klasy 'Employee', 'Student' lub 'Organization'.
    initiator = models.ForeignKey(User, null = True, blank = True, 
                                  verbose_name = _('StateChange/initiator'))
    # dodatkowa informacja nt. zmiany stanu, uzasadnienie decyzji np. odrzucenia tematu
    comment = models.TextField(blank = True, 
                               verbose_name = _('StateChange/comment'))
    occuredAt = models.DateTimeField(default = timezone.now, editable = False, null = True, blank = True, 
                                     verbose_name = _('StateChange/occured at'))
    
    def __unicode__(self):
        return '%s, %s' % (self.get_state_display(), self.initiator)


def attachmentPath(instance, filename):
    u'''
    Generuje trudną do odgadnięcia ścieżkę dla załącznika na podstawie sumy kontrolnej MD5 nazwy pliku sklejonej z czasem jego dodawania.
    '''

    from os import path
    from hashlib import md5

    filename, fileExtension = path.splitext(filename)

    destinationPath = 'attachments/{}/{}{}'.format(md5(filename + unicode(timezone.now())).hexdigest(),
                                                   slugify(filename),
                                                   fileExtension)
    return destinationPath


class Attachment(models.Model):
    class Meta:
        verbose_name = _('Attachment')
        verbose_name_plural = _('Attachments')

    name = models.CharField(max_length = 255, verbose_name = _('Attachment/name'))
    source = models.FileField(upload_to = attachmentPath, verbose_name = _('Attachment/source'))

    def get_absolute_url(self):
        return source.url


