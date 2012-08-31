from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.middleware.gzip import GZipMiddleware

gzip_middleware = GZipMiddleware()

from rfweb.rfwebapp.models import Run
from rfweb.settings import RESULTS_PATH
import sys
import os
import tempfile
import zipfile

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from contextlib import closing
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse
from django.template import loader, Context

class FileWrapperMine(FileWrapper):
    """
    GZipMiddleware FileWrapper fix
    """
    def __iter__(self):
        if hasattr(self.filelike, 'seek'): 
            self.filelike.seek(0) 
        return self 

def results(request):
    def _raw(request):
        runs_all = Run.objects.all().order_by('-id')
        paginator = Paginator(runs_all, 50)
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

def results_csv(request):
    def _raw(request):
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=results.csv'
        t = loader.get_template('results.csv')
        runs_all = Run.objects.all().order_by('-id')
        response.write(t.render(Context({'results': runs_all,})))
        return response
    response = _raw(request)
    return gzip_middleware.process_response(request, response)
    return results_csv

def results_md(request):
    def _raw(request):
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=results.md'
        t = loader.get_template('results.md')
        runs_all = Run.objects.all().order_by('-id')
        response.write(t.render(Context({'results': runs_all,})))
        return response
    response = _raw(request)
    return gzip_middleware.process_response(request, response)
    return results_md

def results_zip(request, resultsname):
    def _raw(request):
        _temp = tempfile.NamedTemporaryFile(delete=False)#TemporaryFile()
        _results_dir = os.path.join(RESULTS_PATH, resultsname)
        print _results_dir, _temp, _temp.name, _temp.tell()
        with closing(zipfile.ZipFile(_temp, 'w', zipfile.ZIP_DEFLATED)) as z:
            print z
            for root, dirs, files in os.walk(_results_dir):
                print root, dirs, files 
                for fn in files:
                    absfn = os.path.join(root, fn)
                    print absfn
                    zfn = absfn[len(_results_dir)+len(os.sep):]
                    z.write(absfn, zfn)
        wrapper = FileWrapperMine(_temp)
        print _temp.tell(), wrapper, dir(wrapper),os.path.getsize(_temp.name)
        response = HttpResponse(wrapper, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=%s.zip' % resultsname 
        response['Content-Length'] = os.path.getsize(_temp.name) #_temp.tell()
        #assert False, response
        _temp.seek(0)
        return response
    response = _raw(request)
    return gzip_middleware.process_response(request, response)
    return results_zip

