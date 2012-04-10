import os.path

from django.conf.urls.defaults import *
from django.conf import settings

from rfweb.rfwebapp import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from dajaxice.core import dajaxice_autodiscover
dajaxice_autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    (r'^%s/' % settings.DAJAXICE_MEDIA_PREFIX, include('dajaxice.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT }),
    (r'^upload/?$', views.upload),
    (r'^search/?$', views.search),
    (r'^suite/(.*)', views.suite),
    (r'^create_task/?$', views.create_task),
    (r'^tasks/?$', views.tasks),
    (r'^log/?$', views.log),
    (r'^$', views.index),
)
