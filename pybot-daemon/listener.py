"""
Listener implementation example. 
Instead of doing nothing listener can, for example, report test status somewhere (e.g., to remote DB).
It also can write custom log file.
"""

import os
import sys
import tempfile
import config
os.environ['DJANGO_SETTINGS_MODULE'] = 'rfweb.settings'
sys.path.append(config.django.app_dir)
from rfweb.rfwebapp.models import Suite, Test, Task, Run, Log, _LOG_TYPE as TYPE

class Listener():
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, filename='listener.log'):
        outpath = os.path.join(tempfile.gettempdir(), filename)
        self.outfile = open(outpath, 'w')
        self.host = 12345678

    def start_suite(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        log = Log(type=TYPE['Start suite'], time=attrs['starttime'], host_id=self.host, suite=name, comment=attrs['longname'])
        log.save()

    def start_test(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        log = Log(type=TYPE['Start test'], time=attrs['starttime'], host_id=self.host, status=attrs['critical'] == 'yes' and True or False, test=name, comment=attrs['doc'])
        log.save()

    def start_keyword(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        log = Log(type=TYPE['Start keyword'], time=attrs['starttime'], host_id=self.host, keyword=name, comment=attrs['doc'])
        log.save()

    def end_suite(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        log = Log(type=TYPE['End suite'], time=attrs['endtime'], host_id=self.host, status=attrs['status'] == 'PASS' and True or False, suite=name, comment=attrs['statistics'])
        log.save()

    def end_test(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        log = Log(type=TYPE['End test'], time=attrs['endtime'], host_id=self.host, status=attrs['status'] == 'PASS' and True or False, test=name, comment=str(attrs))
        log.save()

    def end_keyword(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.outfile.write(_str)
        log = Log(type=TYPE['End keyword'], time=attrs['endtime'], host_id=self.host, status=attrs['status'] == 'PASS' and True or False, keyword=name, comment=str(attrs))
        log.save()

    def log_message(self, message):
        log = Log(type=TYPE['Log message'], host_id=self.host, status=message['html'] == 'yes' and True or False, comment=message['message'])
        log.save()

    def message(self, message):
        log = Log(type=TYPE['Message'], host_id=self.host, status=message['html'] == 'yes' and True or False, comment=message['message'])
        log.save()

    def close(self):
        _str = '[%s]: closing\n' % __file__
        self.outfile.write(_str)
        self.outfile.close()
        log = Log(type=TYPE['Close'], host_id=self.host)
        log.save()

