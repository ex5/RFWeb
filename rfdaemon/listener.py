#!/usr/bin/python2.7

"""
Listener implementation. 
"""

import os
import subprocess
import sys
import tempfile
import config
from uuid import getnode as get_mac
os.environ['DJANGO_SETTINGS_MODULE'] = 'rfweb.settings'
sys.path.append(config.django.app_dir)
from rfweb.rfwebapp.models import Suite, Test, Task, Run, Log, _LOG_TYPE as TYPE
LEN = 250

class Listener():
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self, run_id, uid):
        self.hwaddr = get_mac()
        self.run_id = run_id
        self.uid = uid
    
    def log(self, **kwargs):
        log_entry = Log(run_id=self.run_id, hwaddr=self.hwaddr, **kwargs)
        if 'comment' in kwargs and kwargs['comment'] and not any(map(lambda x: x in kwargs['comment'], ('Created keyword', 'Return: ', 'Imported ', 'Keyword timeout', 'Test timeout', 'Arguments: '))):
            subprocess.call('echo "%s:%s: %s" > /dev/console' % (self.uid, 'status' in kwargs and (kwargs['status'] and 'PASS' or 'FAIL') or '', 'comment' in kwargs and kwargs['comment'].rstrip() or ''), shell=True)
        log_entry.save()

    def start_suite(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.log(type=TYPE['Start suite'], time=attrs['starttime'], suite=name, comment=attrs['longname'][:LEN])

    def start_test(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        self.log(type=TYPE['Start test'], time=attrs['starttime'], status=attrs['critical'] == 'yes' and True or False, suite=attrs['longname'], test=name, comment=attrs['doc'][:LEN])

    def start_keyword(self, name, attrs):
        #_str = '[%s]: %s \n' % (__file__, (str(attrs)))
        #self.log(type=TYPE['Start keyword'], time=attrs['starttime'], keyword=name, comment=attrs['doc'][:LEN])
        pass

    def end_suite(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        status = attrs['status'] == 'PASS' and True or False
        run = Run.objects.get(pk=self.run_id)
        run.status = status
        run.save()
        self.log(type=TYPE['End suite'], time=attrs['endtime'], status=status, suite=name, comment=attrs['statistics'][:LEN])

    def end_test(self, name, attrs):
        _str = '[%s]: %s \n' % (__file__, (str(attrs)))
        status = attrs['status'] == 'PASS' and True or False
        run = Run.objects.get(pk=self.run_id)
        run.status = status
        run.save()
        self.log(type=TYPE['End test'], time=attrs['endtime'], status=attrs['status'] == 'PASS' and True or False, suite=attrs['longname'], test=name, comment=attrs['message'][:LEN])

    def end_keyword(self, name, attrs):
        #_str = '[%s]: %s \n' % (__file__, (str(attrs)))
        #self.log(type=TYPE['End keyword'], time=attrs['endtime'], status=attrs['status'] == 'PASS' and True or False, keyword=name, comment="Elapsed time: %s" % attrs['elapsedtime'])
        pass

    def log_message(self, message):
        #self.log(type=TYPE['Log message'], status=message['html'] == 'yes' and True or False, comment=message['message'][:LEN])
        pass

    def message(self, message):
        #self.log(type=TYPE['Message'], status=message['html'] == 'yes' and True or False, comment=message['message'][:LEN])
        pass

    def close(self):
        _str = '[%s]: closing\n' % __file__
        self.log(type=TYPE['Close'])

