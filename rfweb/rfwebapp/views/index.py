from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.middleware.gzip import GZipMiddleware

gzip_middleware = GZipMiddleware()

from rfweb.rfwebapp.models import Suit
from search import SearchForm
import sys
from rfwebsettings import ROBOTD_PATH
sys.path.append(ROBOTD_PATH)
import robotd

def index(request):
    def _raw(request):
        suits = Suit.objects.all().order_by('name')
        return render_to_response('index.html', 
                {'suits': suits, 'form': SearchForm(), 'status': robotd.check_status()}, context_instance=RequestContext(request))
    response = _raw(request)
    return gzip_middleware.process_response(request, response)
    return index

