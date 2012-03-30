import sys
import os

# path is the parent directory of this script
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# we check for path because we're told to at the tail end of
# http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives#WSGIReloadMechanism 
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % os.path.dirname(os.path.abspath(__file__)).split('/')[-1]
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
