# Create your views here.
from django.http import HttpResponse
import sqlite3
import os
import tempfile
import zipfile
from django.core.servers.basehttp import FileWrapper
from contextlib import closing
import sys
_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
_path not in sys.path and sys.path.append(_path)
from settings import PROJECT_ROOT
import re

def show_brief(request):
    _c = sqlite3.Connection('%s/BFT2.db' % PROJECT_ROOT)
    modules = _c.execute('SELECT * from module where t>="2012-02-29" order by id').fetchall()
    _table = "<table border='5'><tr><td><strong>Serial number</strong></td><td><strong>Number of trials</strong></td><td><strong>Result</strong></td><td><strong>Timestamp</strong></td><td><strong>Download link</strong></td><td><strong>HwAddr 0</strong></td><td><strong>HwAddr 1</strong></td></tr>"
    for _row in modules:
        _hwaddrs = _c.execute('select hwaddr from hwaddr where id="%s"' % _row[0]).fetchall()
        _report_link = None
        if os.path.isdir("%s/reports/%s_%03d" % (PROJECT_ROOT, _row[0], int(_row[1]))):
            _report_link = "d/reports/%(sn)s_%(tr)03d/report_%(sn)s_%(tr)03d.html" % {'sn': _row[0], 'tr': int(_row[1])}
        _table += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (_report_link and '<a href="%s">%s</a>' % (_report_link, _row[0]) or _row[0], _row[1], _row[2] == -1 and "<strong><font color=\"red\">FAIL %d</font></strong>" % _row[2] or _row[2] == 1 and "<font color=\"blue\">LAST %d</font>" % _row[2] or "<strong><font color=\"green\">PASS %d</font></strong>" % _row[2], _row[3], _report_link and "<a href=\"d/tar/%s.tar.gz\">tar.gz</a>" % _report_link.split('/')[2] or '', _hwaddrs and len(_hwaddrs) > 0 and _hwaddrs[0][0] or '', _hwaddrs and len(_hwaddrs) > 1 and _hwaddrs[1][0] or '')
    _table += "</table>"
    return HttpResponse(_table)

def show_report(request):
    return HttpResponse(open(os.path.join(PROJECT_ROOT, "reports") + re.findall("/[\w]+(/.*)", request.path_info)[0]).read())

def download_report(request):
    _archive = request.path_info
    _temp = tempfile.TemporaryFile()
    _report_dir = "%s/reports/%s" % (PROJECT_ROOT, _archive.split('/')[-1][:-7])
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

