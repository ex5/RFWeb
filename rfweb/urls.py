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
    (r'^suit/(.*)', views.suit),
    (r'^create_task/?$', views.create_task),
    (r'^show_tasks/?$', views.show_tasks),
    (r'^$', views.index),
)