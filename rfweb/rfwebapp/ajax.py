from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from rfweb.rfwebapp.models import Suite, Test, Task, Run, Log, LOG_TYPE
from django.utils import simplejson
from forms import LogViewerForm

@dajaxice_register
def get_test_list(request, suite_id):
    dajax = Dajax()
    tests = Test.objects.filter(suite_id__exact=(int(suite_id))).distinct()
    out = ""
    for test in tests:
        out += "<option value='%d'>%s" % (test.id, test)
    dajax.assign('#tests', 'size', len(tests))
    dajax.assign('#tests', 'visibility', 'true')
    dajax.assign('#tests', 'innerHTML', out)
    return dajax.json()

@dajaxice_register
def create_task(request, name, suite_id, test_ids, comment, run):
    if not suite_id:
        return
    dajax = Dajax()
    test_ids = filter(lambda x: bool(x) == True, test_ids.split(','))
    task = Task(suite=Suite.objects.get(id__exact=(int(suite_id))), name=name, comment=comment)
    task.save()
    task.tests.add(*Test.objects.filter(id__in=test_ids))
    task.save()
    _xml = ""
    for test in test_ids:
        _xml += "<test name='%s' />\n" % test
    dajax.assign('#preview', 'rows', len(_xml.split('/')) + 1)
    dajax.assign('#preview', 'cols', max(map(len, _xml.split('/'))) + 1)
    dajax.assign('#preview', 'innerText', _xml)
    if run:
        run = Run(task=task, running=None)
        run.save()
    return dajax.json()

@dajaxice_register
def start_tasks(request, selected):
    dajax = Dajax()
    tasks = Task.objects.filter(id__in=map(int, selected))
    out = "<root>"
    for task in tasks:
        out += '<robot suite="%s" output="%s">' % (task.suite.path, ".")
        for test in task.tests.select_related():
            out += "<test name='%s' />" % test.name
        out += "</robot>"
    out += "root"
    dajax.assign('#start', 'innerHTML', out)
    return dajax.json()

@dajaxice_register
def stop_tasks(request, selected):
    dajax = Dajax()
    return dajax.json()

@dajaxice_register
def delete_tasks(request, selected):
    dajax = Dajax()
    dajax.assign('#show_logs', 'innerText', str(request))
    runs = Run.objects.filter(task_id__in=map(int, selected)).delete()
    tasks = Task.objects.filter(id__in=map(int, selected)).delete()
    dajax.redirect('/tasks/')
    return dajax.json()

@dajaxice_register
def show_task_tests(request, task_id, test_ids):
    dajax = Dajax()
    tests = Test.objects.filter(id__in=map(int, test_ids.replace('L', '').replace('[', '').replace(']', '').split(','))) # quite a temporary solution
    out = "<ul>"
    for test in tests:
        out += "<li>%s</li>" % test.name
    out += "</ul>"
    dajax.assign('#tests_%s' % task_id, 'innerHTML', out)
    return dajax.json()

@dajaxice_register
def show_task_runs(request, task_id):
    dajax = Dajax()
    runs = Run.objects.filter(task__exact=int(task_id))
    out = "<ul>"
    for run in runs:
        out += "<li>%s, %s, %s, %s</li>" % (run.start, run.running, run.status, run.finish)
    out += "</ul>"
    dajax.assign('#tests_%s' % task_id, 'innerHTML', out)
    return dajax.json()

@dajaxice_register
def check_log(request, settings):
    dajax = Dajax()
    settings = LogViewerForm(settings)
    if not settings.data:
        settings = LogViewerForm({'limit': 10, 'filter': map(lambda (x, y): x, LOG_TYPE), 'refresh_timeout': 1})
    logs = Log.objects.filter(type__in=map(int, settings.data['filter'])).order_by('-time')[:settings.data['limit'] or 10]
    dajax.assign('#log', 'innerHTML', logs and '<br>'.join(map(str, logs)) or 'Log is empty')
    return dajax.json()

