from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
from settings import PROJECT_NAME

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'all/reports/(?P<x>.*.html)$', redirect_to, {'url': '/reports/%(x)s'}),
    (r'all/tar/(?P<x>.*.tar.gz)$', redirect_to, {'url': '/tar/%(x)s'}),
    url('^$', '%s.viewer.views.show_table' % PROJECT_NAME, name='home'),
    url(r'reports/*', '%s.viewer.views.show_report' % PROJECT_NAME, name='report'),
    url(r'mark/', '%s.viewer.views.mark' % PROJECT_NAME, name='mark'),
    url(r'all/csv/', '%s.viewer.views.csv_all' % PROJECT_NAME, name='export csv all'),
    url(r'csv/', '%s.viewer.views.csv' % PROJECT_NAME, name='export csv'),
    url(r'all/', '%s.viewer.views.show_all' % PROJECT_NAME, name='all'),
    url(r'.*tar.gz$', '%s.viewer.views.download_report' % PROJECT_NAME, name='download'),
    # url(r'^BFT2/', include('BFT2.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
