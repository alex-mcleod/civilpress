# Django settings for civilpress project.
from os.path import abspath 
import os 
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Alexander McLeod', 'alxmcleod@gmail.com'),
)

HOME_URL = "http://www.civilpress.org/"

AUTH_PROFILE_MODULE = 'userprofiles.models.UserProfile'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'civilpress_db',                      # Or path to database file if using sqlite3.
        'USER': 'civilpress_admin',                      # Not used with sqlite3.
        'PASSWORD': 'mi211alex',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = '/home/civilpress_admin/civilpress.org/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
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
SECRET_KEY = 'l&-pv8mpaa0@%32dfb&n&-6shs#_ol^ugrl%fdi^_7n#0atbhf'

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
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/civilpress_admin/civilpress.org/templates",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    'django.contrib.comments',
    'south',
    'haystack',
    'endless_pagination',
    'userprofiles',
    'simple_comments',
    'articles',

)

# Determine app to use for commenting. Only necessary if custom app is used. 
COMMENTS_APP = 'simple_comments'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
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

# Include the request context process in templates so that {{ user }} is availabile in every template. 
TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    'django.core.context_processors.request',
)

# Setting for django-endless-pagination app. Determines how many items to show per page. 
ENDLESS_PAGINATION_PER_PAGE = 4

# Settings for Haystack.
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'whoosh_index'),
    },
}

HAYSTACK_SEARCH_RESULTS_PER_PAGE = ENDLESS_PAGINATION_PER_PAGE

# Settings for Facebook registration plugin. 
FACEBOOK_APP_ID = '360618173996495' 
FACEBOOK_APP_SECRET = '5d576076b53d4e6122468119049c6030'
AUTHENTICATION_BACKENDS = ('backends.EmailAuthBackend',)

# Email settings. NOTE: Email is not currently working. 
EMAIL_HOST = 'www.gmail.com'
EMAIL_PORT = 25
EMAIL_HOST_USER = 'alxmcleod'
EMAIL_HOST_PASSWORD = 'mi211alex'
EMAIL_SUBJECT_PREFIX = '[CivilPress.org] '

# The following variables are used in choice fields across the site. 
DISCIPLINE_CHOICES = (
	('History', 'History'),
    ('Linguistics', 'Linguistics'),
    ('Literature', 'Literature'),
    ('Creative writing', 'Creative writing'),
    ('Criminology', 'Criminology'),
    ('Performing arts', 'Performing arts'),
    ('Philosophy', 'Philosophy'),
    ('Religious studies', 'Religious studies'),
    ('Visual arts', 'Visual arts'),
    ('Anthropology', 'Anthropology'),
    ('Archaeology', 'Archaeology'),
    ('Area studies', 'Area studies'),
    ('Cultural and ethnic studies', 'Cultural and ethnic studies'),
    ('Economics', 'Economics'),
    ('Gender and sexuality studies', 'Gender and sexuality studies'),
    ('Geography', 'Geography'),
    ('Politcial science', 'Political science'),
    ('Psychology', 'Psychology'),
    ('Sociology', 'Sociology'),
    ('Space science', 'Space science'),
    ('Earth sciences', 'Earth sciences'),
    ('Life sciences', 'Life sciences'),
    ('Chemistry', 'Chemistry'),
    ('Physics', 'Physics'),
    ('Computer sciences', 'Computer sciences'),
    ('Logic', 'Logic'),
    ('Mathematics', 'Mathematics'),
    ('Statistics', 'Statistics'),
    ('System science', 'Systems science'),
    ('Agriculture', 'Agriculture'),
    ('Architecture and design', 'Architecture and design'),
    ('Business', 'Business'),
    ('Education', 'Education'),
    ('Engineering', 'Engineering'),
    ('Environmental studies', 'Environmental studies'),
    ('Consumer science', 'Consumer science'),
    ('Health science', 'Health science'),
    ('Physical performance studies', 'Physical performance studies'),
    ('Media & communication', 'Media & communication'),
    ('Law', 'Law'),
	)

EDUCATION_LEVEL_CHOICES = (
    ('year7to11', 'High school (years 7-11)'),
    ('year12', 'High school (year 12)'),
    ('UG', 'Undergraduate'),
    ('UGH', 'Undergraduate (honors)'),
    ('PG', 'Postgraduate'),
    ('None', 'None')
	)

GRADE_CHOICES = (
    ('0-49%', '0-49%'),
    ('50-64%', '50-64%'),
    ('65-69%', '65-69%'),
    ('70-74%', '70-74%'),
    ('75-79%', '75-79%'),
    ('80-100%', '80-100%'),
	)

TOPIC_CHOICES = (
	('Problem', 'Problem'),
	('Suggestion', 'Suggestion'),
	('Other','Other'),
	)

ANON_CHOICES = (
    (True, "Yes"),
    (False, "No")
)
