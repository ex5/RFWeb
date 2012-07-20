#!/usr/bin/python2.7

import sys
import time
import os
import daemon
import config
import subprocess
import threading
os.environ['DJANGO_SETTINGS_MODULE'] = 'rfweb.settings'
sys.path.append(config.django.app_dir)
import rfweb.settings
from rfweb.rfwebapp.models import Suite, Test, Task, Run, Log
from uuid import getnode as get_mac
import datetime
import syslog

WAT_TIME = 10

class Task(object):
    def __init__(self, parent, run_id, on_exit, args):
        self.parent = parent
        self.on_exit = on_exit
        self.args = args
        self.my_run = Run.objects.get(pk=run_id)
        syslog.syslog(syslog.LOG_NOTICE, "RobotD task initialized: %s, %s" % (on_exit, args))
        self.run_task()

    def run_task(self):
        """
        Runs the given args in a subprocess.Popen, calls the function on_exit when the subprocess completes.
        on_exit is a callable object;
        args is a list/tuple of args that would be given to subprocess.Popen.
        """
        def run_in_thread(on_exit, args):
            proc = subprocess.Popen(*args)
            proc.wait()
            on_exit(proc)
            syslog.syslog(syslog.LOG_NOTICE, "Results path is: %s" % args[0][args[0].index('--outputdir') + 1])
            self.my_run.status = (proc.returncode == 0) and True or False
            self.my_run.finish = datetime.datetime.now()
            self.my_run.save()
            return
        self.thread = threading.Thread(target=run_in_thread, args=(self.on_exit, self.args))
        self.thread.start()

    def finish(self):
        pass
        
def on_exit(process):
    syslog.syslog(syslog.LOG_DEBUG, "%s" % process.stderr.read())
    syslog.syslog(syslog.LOG_DEBUG, "RobotD task %s has finished with returncode %s" % (process.pid, process.returncode))

class RobotDaemon(daemon.Daemon):
    def __init__(self, *argv, **kwargs):
        super(RobotDaemon, self).__init__(*argv, **kwargs)
        syslog.syslog(syslog.LOG_DEBUG, "%s" % config.path)
        self.hwaddr = get_mac()
        self.uid = subprocess.Popen('modprobe ipmi_si && modprobe ipmi_devintf && ipmitool fru | grep "Board Serial" | sed "s/.*: \(.*\)/\\1/"', shell=True, stdout=subprocess.PIPE)
        try:
            last_time = time.time()
            while self.uid.poll() == None:
                if (time.time() - last_time) > WAT_TIME:
                    syslog.syslog("%s, %s: %s" % (__name__, 'Waited long enough'))
                    break
            if self.uid.poll() != None:
                self.uid = self.uid.stdout.read().split('\n')[0]
        except Exception, e:
            self.uid = None
            syslog.syslog(syslog.LOG_ERROR, 'Cannot fetch host UID: %s' % e)
        self.ip = subprocess.Popen("ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'", shell=True, stdout=subprocess.PIPE)
        try:
            last_time = time.time()
            while self.ip.poll() == None:
                if (time.time() - last_time) > WAT_TIME:
                    syslog.syslog("%s, %s: %s" % (__name__, 'Waited long enough'))
                    break
            if self.ip.poll() != None:
                self.ip = self.ip.stdout.read().split('\n')[0]
        except Exception, e:
            self.ip = None
            syslog.syslog(syslog.LOG_ERROR, 'Cannot fetch host IP: %s' % e)
        syslog.syslog(syslog.LOG_DEBUG, 'IP: %s, MAC: %s, UID: %s' % (self.ip, self.hwaddr, self.uid))

    def reload_config(self):
        try:
            for main_run in Run.objects.filter(hwaddr=None):
                i = 0
                task = main_run.task
                main_run_id = main_run.pk
                my_runs = Run.objects.filter(hwaddr=self.hwaddr, task=task, rerun=False)
                if my_runs:
                    continue
                my_run = Run(task_id=main_run.task.pk, hwaddr=self.hwaddr, ip=self.ip, uid=self.uid)
                my_run.save()
                _id = "%s_%04d_%s" % (task.name, my_run.pk, self.ip)
                _cmd = ['python2.7', config.path.pybot, '--critical', 'critical', '--pythonpath', "%s:%s" % (config.path.listener_path, config.path.suits_path), '--listener',
                        "%(module)s:%(run_id)s" % {'module': config.path.listener, 'run_id': my_run.pk}]
                _suites = set()
                for test in task.tests.all():
                    _cmd += ['--test', test.name]
                    _suites.add(test.suite.path)
                _outputdir = my_run.path_to_results
                _cmd += ['--outputdir', _outputdir]
                _cmd += _suites
                if not os.path.isdir(_outputdir):
                    os.mkdir(_outputdir)
                Task(self, my_run.pk, on_exit, (_cmd, 0, None, None, subprocess.PIPE, subprocess.PIPE))
        except Exception, e:
            syslog.syslog(syslog.LOG_DEBUG, "Cannot fetch tasks: %s, %s" % (e.message, e.args))

    def quit(self):
        syslog.syslog(syslog.LOG_NOTICE, 'exiting')
        self.stop()

    def run(self):
        while True:
            time.sleep(2)
            self.reload_config()

robotd_init = lambda: RobotDaemon(pidfile=config.path.pid_file % get_mac(), 
                         stdout=config.path.stdout, 
                         stderr=config.path.stderr)

def check_status():
    robotd = robotd_init()
    return robotd.status()

def main():
    robotd = robotd_init()
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            robotd.start()
        elif 'stop' == sys.argv[1]:
            robotd.stop()
        elif 'restart' == sys.argv[1]:
            robotd.restart()
        elif 'status' == sys.argv[1]:
            print robotd.status() and "Running" or "Not running"
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart|status" % sys.argv[0]
        sys.exit(2)

if __name__ == "__main__":
    main()

