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
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
    (r'^upload/?$', views.upload),
    (r'^search/?$', views.search),
    (r'^suite/(.*)', views.suite),
    (r'^suite_csv/(.*)', views.suite_csv),
    (r'^suite_md/(.*)', views.suite_md),
    (r'^create_task/?$', views.create_task),
    (r'^tasks/?$', views.tasks),
    (r'^results/$', views.results),
    (r'^download/([\w\d_-]+_[\d-]+_[\d]+).zip', views.results_zip),
    (r'results/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.RESULTS_PATH, 'show_indexes':True}),
    (r'^log/?$', views.log),
    (r'^$', views.index),
)
