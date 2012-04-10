from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.middleware.gzip import GZipMiddleware

gzip_middleware = GZipMiddleware()

from rfweb.rfwebapp.models import Task
from django.core import serializers

def tasks(request):
    def _raw(request):
        return render_to_response('tasks.html', {'tasks': serializers.serialize("python", Task.objects.all())}, context_instance=RequestContext(request))
    response = _raw(request)
    return gzip_middleware.process_response(request, response)
    return tasks

