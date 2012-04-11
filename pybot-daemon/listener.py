"""
Listener implementation. 
"""

import os
import sys
import tempfile
import config
from uuid import getnode as get_mac
os.environ['DJANGO_SETTINGS_MODULE'] = 'rfweb.settings'
sys.path.append(config.django.app_dir)
from rfweb.rfwebapp.models import Suite, Test, Task, Run, Log, _LOG_TYPE as TYPE

class Listener():
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, task_id, filename='listener.log'):
        outpath = os.path.join(tempfile.gettempdir(), filename)
        self.outfile = open(outpath, 'w')
        self.host_id = get_mac()
        self.task_id = task_id
        self.outfile.write("host: %s,  task: %s" % (self.host_id, self.task_id))
    
    def log(self, **kwargs):
        log_entry = Log(task_id=self.task_id, host_id=self.host_id, **kwargs)
        log_entry.save()

    def start_suite(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        self.log(type=TYPE['Start suite'], time=attrs['starttime'], suite=name, comment=attrs['longname'])

    def start_test(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        self.log(type=TYPE['Start test'], time=attrs['starttime'], status=attrs['critical'] == 'yes' and True or False, test=name, comment=attrs['doc'])

    def start_keyword(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        self.log(type=TYPE['Start keyword'], time=attrs['starttime'], keyword=name, comment=attrs['doc'])

    def end_suite(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        self.log(type=TYPE['End suite'], time=attrs['endtime'], status=attrs['status'] == 'PASS' and True or False, suite=name, comment=attrs['statistics'])

    def end_test(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        self.log(type=TYPE['End test'], time=attrs['endtime'], status=attrs['status'] == 'PASS' and True or False, test=name, comment=attrs['message'])

    def end_keyword(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        self.log(type=TYPE['End keyword'], time=attrs['endtime'], status=attrs['status'] == 'PASS' and True or False, keyword=name, comment="Elapsed time: %s" % attrs['elapsedtime'])

    def log_message(self, message):
        self.log(type=TYPE['Log message'], status=message['html'] == 'yes' and True or False, comment=message['message'])

    def message(self, message):
        self.log(type=TYPE['Message'], status=message['html'] == 'yes' and True or False, comment=message['message'])

    def close(self):
        _str = '[%s]: closing\n' % __file__
        self.outfile.write(_str)
        self.outfile.close()
        self.log(type=TYPE['Close'], host_id=self.host_id)

