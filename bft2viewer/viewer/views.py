# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
import sqlite3
import os
import tempfile
import zipfile
from django.core.servers.basehttp import FileWrapper
from contextlib import closing
from django.shortcuts import render_to_response, render
import sys
_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
_path not in sys.path and sys.path.append(_path)
from settings import PROJECT_ROOT
import re

href = lambda link, text: {'link': link, 'text': text}
states = {'FAIL': -1, 'PASS': 0, 'RETEST': 2, 'HIDE': 3, 'LAST': 1}
_states = {states[y]: y for y in states}

def mark(request):
    if request.method == 'POST': # If the form has been submitted...
        _new_state = request.POST['state']
        MMs = map(lambda x: x.split(','), filter(lambda x: x != 'state', request.POST.keys()))
        _c = sqlite3.Connection('%s/BFT2.db' % PROJECT_ROOT)
        _tmp = ''
        for _mm_id, _trial in MMs:
            _sql = 'UPDATE module SET state = "%d" WHERE id="%s" AND trial="%d"' % (states[_new_state], _mm_id, int(_trial))
            _tmp += _sql
            _c.execute(_sql)
        _c.commit()
        _c.close()
        return HttpResponseRedirect ('/d/')

def show_table(request):
    _c = sqlite3.Connection('%s/BFT2.db' % PROJECT_ROOT)
    modules = _c.execute('SELECT * FROM module WHERE t>="2012-02-29" AND state != "%d" ORDER BY id' % states['HIDE']).fetchall()
    _header = "Serial number,Number of trials,Result,Timestamp,Download link,HwAddr 0,HwAddr 1".split(",")
    _table = []
    for _row in modules:
        _hwaddrs = _c.execute('SELECT hwaddr FROM hwaddr WHERE id="%s"' % _row[0]).fetchall()
        _report_link = None
        if os.path.isdir("%s/reports/%s_%03d" % (PROJECT_ROOT, _row[0], int(_row[1]))):
            _report_link = "reports/%(sn)s_%(tr)03d/report_%(sn)s_%(tr)03d.html" % {'sn': _row[0], 'tr': int(_row[1])}
        _table.append((href(_report_link, _row[0]),
                       _row[1],
                       _states[_row[2]],
                       _row[3],
                       href(_report_link and "tar/%s.tar.gz" % _report_link.split('/')[1] or '', "tar.gz"), 
                       _hwaddrs and len(_hwaddrs) > 0 and _hwaddrs[0][0] or '', 
                       _hwaddrs and len(_hwaddrs) > 1 and _hwaddrs[1][0] or ''))
    return render_to_response("table_simple.html", {'header': _header, "table": _table})

def show_report(request):
    return HttpResponse(open(PROJECT_ROOT + request.path_info).read())

def download_report(request):
    _archive = request.path_info
    _temp = tempfile.TemporaryFile()
    _report_dir = "%s/reports/%s" % (PROJECT_ROOT, _archive.split('/')[-1][:-7])
    #return HttpResponse(_report_dir)
    with closing(zipfile.ZipFile(_temp, 'w', zipfile.ZIP_DEFLATED)) as z:
        for root, dirs, files in os.walk(_report_dir):
            for fn in files:
                absfn = os.path.join(root, fn)
                zfn = absfn[len(_report_dir)+len(os.sep):]
                z.write(absfn, zfn)
    wrapper = FileWrapper(_temp)
    response = HttpResponse(wrapper, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename=%s.zip' % _archive.split('/')[-1][:-7]
    response['Content-Length'] = _temp.tell()
    _temp.seek(0)
    return response

