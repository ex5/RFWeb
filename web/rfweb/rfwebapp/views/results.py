from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.middleware.gzip import GZipMiddleware

gzip_middleware = GZipMiddleware()

from rfweb.rfwebapp.models import Run
import sys

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def results(request):
    def _raw(request):
        runs_all = Run.objects.all().order_by('-id')
        paginator = Paginator(runs_all, 15)
        page = request.GET.get('page')
        try:
            runs = paginator.page(page != None and page or 1)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            runs = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            runs = paginator.page(paginator.num_pages)
        return render_to_response('results.html', 
                {'results': runs}, context_instance=RequestContext(request))
    response = _raw(request)
    return gzip_middleware.process_response(request, response)
    return results

