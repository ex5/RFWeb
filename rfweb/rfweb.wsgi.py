# Template file for RFWeb deployment with wsgi. 

# List paths to be added to PYTHONPATH. At least the installation directory
# (normally site-packages) should be added
PATHS = []
# You shouldn't need to edit the code below.
import os
import sys

PATHS = [os.path.abspath(os.path.dirname(__file__)), os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
for path in PATHS:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'rfweb.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

