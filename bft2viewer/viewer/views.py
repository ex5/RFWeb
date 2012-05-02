# Create your views here.
import sys
import os
_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
_path not in sys.path and sys.path.append(_path)
from settings import PROJECT_ROOT
import sqlite3
import tempfile
import zipfile
import re
import time
from contextlib import closing
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import loader, Context

Href = lambda link, text: {'link': link, 'text': text}
STATE = {'FAIL': -1, 'PASS': 0, 'RETEST': 2, 'HIDE': 3, 'LAST': 1}
NUMSTATE = {STATE[y]: y for y in STATE}
DB_PATH = '%s/BFT2.db' % PROJECT_ROOT
ORIGINAL_DB_PATH = '%s/BFT2.original.db' % PROJECT_ROOT

# ------------------------------------------- ## --------------------------------------- #
def _append_new(request):
    _tmp = ""
    _c = sqlite3.Connection(DB_PATH)
    _c_original = sqlite3.Connection(ORIGINAL_DB_PATH)
    _sql_count = 'SELECT COUNT(*) FROM module'
    _current_count = _c.execute(_sql_count).fetchall()
    _current_count = _current_count and len(_current_count) > 0 and int(_current_count[0][0])
    _new_count = _c_original.execute(_sql_count).fetchall()
    _new_count = _new_count and len(_new_count) > 0 and int(_new_count[0][0])
    if _new_count <= _current_count:
        return HttpResponse('no new entries')
    _sql = 'SELECT * FROM module'
    for MM in _c_original.execute(_sql).fetchall():
        _sql = 'SELECT * FROM module WHERE id="%s" AND trial=%d' % (MM[0], MM[1])
        if not _c.execute(_sql).fetchall():
            _tmp += _sql
            _tmp += '<br>'
            _sql = 'INSERT INTO module (id, trial, state, t, comment, show) VALUES("%s", %d, %d, "%s", "", 1)' % tuple(MM)
            _tmp += _sql
            _tmp += '<br><br>'
            _c.execute(_sql)
            _c.commit()
    _c.close()
    _c_original.close()
    return HttpResponse(_tmp)

def _fetch_data(fetch_all=False, export=False):
    _c = sqlite3.Connection(DB_PATH)
    _c_original = sqlite3.Connection(ORIGINAL_DB_PATH)
    _sql = 'SELECT id, trial, state, t, comment FROM module WHERE t>="2012-02-29" AND show > 0 ORDER BY id'
    if fetch_all:
       _sql =  'SELECT id, trial, state, t, comment FROM module ORDER BY id'
    mms = _c.execute(_sql).fetchall()
    _header = "Serial number,Trial#,Result,New result,Timestamp,Logs,HwAddr 0,HwAddr 1,Comment, New comment".split(",")
    _table = []
    if export:
        _header = "Serial number,Trial#,Result,New result,Timestamp,HwAddr 0,HwAddr 1,Comment".split(",")
        _table.append(_header)
    for _row in mms:
        _hwaddrs = _c_original.execute('SELECT hwaddr FROM hwaddr WHERE id="%s"' % _row[0]).fetchall()
        mm_original_state = _c_original.execute('SELECT state FROM module WHERE id = "%s" AND trial = %d' % (_row[0], _row[1])).fetchall()
        if export:
            _table.append((_row[0], _row[1], 
                       NUMSTATE[mm_original_state[0][0]], NUMSTATE[_row[2]], _row[3],
                       _hwaddrs and len(_hwaddrs) > 0 and _hwaddrs[0][0] or '', 
                       _hwaddrs and len(_hwaddrs) > 1 and _hwaddrs[1][0] or '',
                       _row[4])
                       )
            continue
        _report_link = None
        if os.path.isdir("%s/reports/%s_%03d" % (PROJECT_ROOT, _row[0], int(_row[1]))):
            _report_link = "reports/%(sn)s_%(tr)03d/report_%(sn)s_%(tr)03d.html" % {'sn': _row[0], 'tr': int(_row[1])}
        _table.append((Href(_report_link, _row[0]),
                       _row[1],
                       NUMSTATE[mm_original_state[0][0]],
                       NUMSTATE[_row[2]],
                       _row[3],
                       Href(_report_link and "tar/%s.tar.gz" % _report_link.split('/')[1] or '', "tar.gz"), 
                       _hwaddrs and len(_hwaddrs) > 0 and _hwaddrs[0][0] or '', 
                       _hwaddrs and len(_hwaddrs) > 1 and _hwaddrs[1][0] or '',
                       _row[4])
                       )
    _c.close()
    _c_original.close()
    return {'header': _header, "table": _table}

# ------------------------------------------- ## --------------------------------------- #
def csv(request):
    #raise False, request
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=BFT2_%s.csv' % time.time()
    t = loader.get_template('simple.csv')
    c = Context({'data': _fetch_data(export=True)["table"],})
    response.write(t.render(c))
    return response

def csv_all(request):
    #raise False, request
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=BFT2_full_%s.csv' % time.time()
    t = loader.get_template('simple.csv')
    c = Context({'data': _fetch_data(fetch_all=True, export=True)["table"],})
    response.write(t.render(c))
    return response

def mark(request):
    if request.method == 'POST':
        MMs = lambda: map(lambda x: x.split(','), filter(lambda x: x not in ('state', 'hide') and "new comment" not in x, request.POST.keys()))
        _tmp = ''
        if 'hide' in request.POST:
            _c = sqlite3.Connection(DB_PATH)
            for _mm_id, _trial in MMs():
                _sql = 'UPDATE module SET show = 0 WHERE id="%s" AND trial=%d' % (_mm_id, int(_trial))
                _tmp += _sql
                _c.execute(_sql)
            _c.commit()
            _c.close()
        if 'state' in request.POST:
            _new_state = request.POST['state']
            _c = sqlite3.Connection(DB_PATH)
            for _mm_id, _trial in MMs():
                _sql = 'UPDATE module SET state = %d, show = 1 WHERE id="%s" AND trial=%d' % (STATE[_new_state], _mm_id, int(_trial))
                _tmp += _sql
                _c.execute(_sql)
            _c.commit()
            _c.close()
        _f = lambda x: "new comment" in x and len(request.POST[x]) > 0
        if any(map(_f, request.POST.keys())):
            _c = sqlite3.Connection(DB_PATH)
            for _input_name in filter(_f, request.POST.keys()):
                _mm_id, _trial = tuple(_input_name.split(',')[1:])
                _sql = 'UPDATE module SET comment = "%s" WHERE id="%s" AND trial=%d' % (request.POST[_input_name], _mm_id, int(_trial))
                _c.execute(_sql)
            _c.commit()
            _c.close()
    return HttpResponseRedirect('/')

def show_table(request):
    _append_new(request)
    return render_to_response("table_simple.html", _fetch_data())

def show_all(request):
    _append_new(request)
    return render_to_response("table_simple.html", _fetch_data(fetch_all=True))

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

