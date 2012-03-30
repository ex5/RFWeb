from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.middleware.gzip import GZipMiddleware

gzip_middleware = GZipMiddleware()

from rfweb.rfwebapp.models import Suit

def create_task(request):
    def _raw(request):
        suits = Suit.objects.all()
        return render_to_response('create_task.html', {'suits': suits, }, context_instance=RequestContext(request))
    response = _raw(request)
    return gzip_middleware.process_response(request, response)
    return index

