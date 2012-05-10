from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.middleware.gzip import GZipMiddleware

gzip_middleware = GZipMiddleware()

from rfweb.rfwebapp.models import Suite

def create_task(request):
    def _raw(request):
        suites = Suite.objects.all()
        return render_to_response('create_task.html', {'suites': suites, }, context_instance=RequestContext(request))
    response = _raw(request)
    return gzip_middleware.process_response(request, response)
    return index

