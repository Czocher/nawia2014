# -*- coding: utf-8 -*-

# Django settings for Nawia2014 project.
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'nawia.db',
    },
}
DATABASE_ROUTERS = ['ldapdb.router.Router']

TIME_ZONE = 'Europe/Warsaw'
LANGUAGE_CODE = 'pl-pl'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'n(bd1f1c%e8=_xad02x5qtfn%wgwpi492e$8_erx+d)!tpeoim'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'Nawia2014.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'Nawia2014.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
     os.path.join(BASE_DIR, 'templates').replace('\\','/'),
)

INSTALLED_APPS = (
    'suit_localize',
    'suit',
    'django_forms_bootstrap',
    'django_admin_bootstrapped.bootstrap3',
    'django_admin_bootstrapped',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ldapsync',
    'nawia',
    'faculty',
    'reviews',
    'theses',
    'topics',
    'authorships',
    'student',
    'db_tools',
)

# ustawienia autentykacji przez LDAP
import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_LDAP_SERVER_URI = "ldap://ldap.wi.pb.edu.pl:10389"
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=people,ou=FCS,o=BUT,c=pl", ldap.SCOPE_SUBTREE, "(uid=%(user)s)")
AUTH_LDAP_BIND_AS_AUTHENTICATING_USER=True

AUTH_LDAP_BIND_DN = "uid=nawiaagent,ou=agents,ou=FCS,o=BUT,c=pl"
AUTH_LDAP_BIND_PASSWORD = "Nawia2014"

# sterowanie grupami w aplikacji z LDAP - w naszym przypadku nie jest to używane
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=nawiagroups,ou=groups,ou=FCS,o=BUT,c=pl", ldap.SCOPE_SUBTREE, "(objectClass=groupOfNames)")
AUTH_LDAP_MIRROR_GROUPS=True

# mapowanie atrybutów użytkowników LDAP na pola klasy 'User'
AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail",
}
# aktualizacja atrybutów użytkownika przy każdym logowaniu
AUTH_LDAP_ALWAYS_UPDATE_USER = True


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

#Konfiguracja Django Suit (szablon panelu administracyjnego)
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

SUIT_CONFIG = {
    'ADMIN_NAME': 'Admin',
    'HEADER_DATE_FORMAT': 'l, j E Y',
    'HEADER_TIME_FORMAT': 'H:i',
    'SEARCH_URL': '',
    'MENU_OPEN_FIRST_CHILD': False,
    'MENU': (
        '-',
        {'app': 'auth'},
        {'app': 'sites'},
        '-',
        {'app': 'faculty'},
        {'app': 'topics'},
        {'app': 'authorships'},
        {'app': 'theses'},
        {'app': 'reviews'},
    ),
}
