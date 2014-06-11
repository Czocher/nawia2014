# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
import logging
from ldapsync.ldapsync import LdapSync
from itertools import izip

class Command(BaseCommand):
    args = '<log_level>'
    help = '''
           Przeprowadza synchronizacje wlasnej bazy danych serwisu z zewnetrzna
           baza LDAP. Opcjonalny parametr <log_level> okresla minimalny poziom
           komunikatow wypisywanych na konsole.
           Dostepne opcje: NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL.
           Domyslnym poziomem jest INFO.
           '''

    log_levels = {
        'NOTSET': logging.NOTSET,
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    def handle(self, *args, **options):
        # przygotuj loggera wypisującego komunikaty na konsolę (być może ma on przypisane jeszcze inne handlery)
        logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(self.stdout)
        handler.setFormatter(self.PolishUnicodeToAsciiFormatter())
        logger.addHandler(handler)
        #ustaw poziom logowania
        if len(args) > 0 and args[0] in self.log_levels:
            logger.setLevel(self.log_levels[args[0]])
        else:
            logger.setLevel(logging.INFO)
        #uruchom synchronizację
        LdapSync.sync(logger)


    class PolishUnicodeToAsciiFormatter(logging.Formatter):
        u'''
        Formatter dla loggera - zamienia wszystkie "polskie" znaki w komunikatach
        na ich odpowiedniki w alfabecie łacińskim. Zapewnia czytelność komunikatów
        w konsoli (komendy uruchamiają sie z angielskim locale, więc domyślnie
        polskie znaki zamieniają się w krzaki).
        '''
        def format(self, record):
            return '%s: %s' % (record.levelname, self.__convertPolishUnicode(record.msg % record.args))

        @classmethod
        def __convertPolishUnicode(cls, data):
            transFrom = u'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ'
            transTo = u'acelnoszzACELNOSZZ'
            trans = dict((ord(tf), tt) for tf, tt in izip(transFrom, transTo))
            return data.translate(trans)