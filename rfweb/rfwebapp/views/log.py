from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.middleware.gzip import GZipMiddleware

gzip_middleware = GZipMiddleware()

from rfweb.rfwebapp.models import Log
from django.core import serializers
from rfweb.rfwebapp.forms import LogViewerForm

def log(request):
    def _raw(request):
        return render_to_response('log.html', {'viewer_settings': LogViewerForm()}, context_instance=RequestContext(request))
    response = _raw(request)
    return gzip_middleware.process_response(request, response)
    return log

