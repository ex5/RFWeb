from dajax.core import Dajax
from dajaxice.decorators import dajaxice_register
from rfweb.rfwebapp.models import Suite, Test, Task, Run, Log, LOG_TYPE
from django.utils import simplejson
from forms import LogViewerForm
from rfweb.settings import RESULTS_PATH
import shutil
import os

COLORIZE = {'FAIL': '<font color="red">FAIL</font>',
            'PASS': '<font color="green">PASS</font>',
            'Non critical': '<font color="green">Non critical</font>',
            'Critical': '<font color="red">Critical</font>',
}

@dajaxice_register
def get_test_list(request, suite_id):
    dajax = Dajax()
    tests = Test.objects.filter(suite__exact=(int(suite_id))).distinct()
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
        run = Run(task=task, hwaddr=None)
        run.save()
    return dajax.json()

@dajaxice_register
def start_tasks(request, selected):
    dajax = Dajax()
    main_runs = Run.objects.filter(task__in=map(int, selected), hwaddr=None).delete()
    runs = Run.objects.filter(task__in=map(int, selected)).update(rerun=True)
    for task_id in map(int, selected):
        new_run = Run(task=Task.objects.get(id=task_id), hwaddr=None)
        new_run.save()
    dajax.redirect('/tasks/')
    return dajax.json()

@dajaxice_register
def stop_tasks(request, selected):
    dajax = Dajax()
    runs = Run.objects.filter(task__in=map(int, selected), hwaddr=None).delete()
    dajax.redirect('/tasks/')
    return dajax.json()

@dajaxice_register
def delete_tasks(request, selected):
    dajax = Dajax()
    tasks = Task.objects.filter(id__in=map(int, selected)).delete()
    runs = Run.objects.filter(task__in=map(int, selected)).delete()
    dajax.redirect('/tasks/')
    return dajax.json()

@dajaxice_register
def delete_runs(request, selected):
    dajax = Dajax()
    runs = Run.objects.filter(id__in=map(int, selected))
    for run in runs:
        try:
            shutil.rmtree(os.path.join(RESULTS_PATH, run.path_to_results))
        except Exception, e:
            assert False, 'ERROR: %s' % e
    run = Run.objects.filter(id__in=map(int, selected)).delete()
    dajax.redirect('/results/')
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
    runs = Run.objects.filter(task__exact=int(task_id)).order_by('start')
    out = "<ul>"
    for run in runs:
        out += "<li>%s</li>" % str(run)
    out += "</ul>"
    dajax.assign('#runs_%s' % task_id, 'innerHTML', out)
    return dajax.json()

@dajaxice_register
def check_log(request, settings):
    dajax = Dajax()
    settings = LogViewerForm(settings)
    if not settings.data:
        settings = LogViewerForm({'limit': 10, 'filter': map(lambda (x, y): x, LOG_TYPE), 'refresh_timeout': 1})
    logs = Log.objects.filter(type__in=map(int, settings.data['filter'])).order_by('-time')[:settings.data['limit'] or 10]
    if settings.data['host']:
        logs = filter(lambda x: settings.data['host'] in hex(x.hwaddr), logs)

    task = settings.data['task']
    if task:
        logs = filter(lambda x: x.task and task in x.task.name or False, logs)

    test = settings.data['test']
    if test:
        logs = filter(lambda x: x.test and test in x.test or False, logs)

    suite = settings.data['suite']
    if suite:
        logs = filter(lambda x: x.suite and suite in x.suite or False, logs)

    logs = logs and '<br>'.join(map(unicode, logs)) or 'Log is empty'
    for _str in COLORIZE:
        logs = logs.replace(_str, COLORIZE[_str])
    dajax.assign('#log', 'innerHTML', logs)
    return dajax.json()

