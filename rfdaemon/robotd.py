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

class Task(object):
    def __init__(self, parent, run_id, on_exit, args):
        self.parent = parent
        self.on_exit = on_exit
        self.args = args
        #self.run_obj = Run.objects.get(pk=run_id)
        self.my_run = Run.objects.get(pk=run_id)
        syslog.syslog(syslog.LOG_NOTICE, "task initialized: %s, %s" % (on_exit, args))
        # -------- #
        #self.my_run = Run(task_id=self.run_obj.task.pk, hwaddr=self.parent.hwaddr, ip=self.parent.ip, status=True)
        #self.my_run.save()
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
            self.my_run.status = False
            self.my_run.finish = datetime.datetime.now()
            self.my_run.save()
            """
            try:
                self.parent.tasks.remove(self)
            except Exception, e:
                syslog.syslog(syslog.LOG_WARNING, "Task had been removed already or else: %s" % e)
            """
            return
        self.thread = threading.Thread(target=run_in_thread, args=(self.on_exit, self.args))
        self.thread.start()

    def finish(self):
        pass
        
def on_exit(process):
    syslog.syslog(syslog.LOG_DEBUG, "%s" % process.stdout.read())
    syslog.syslog(syslog.LOG_DEBUG, "%s" % process.stderr.read())
    syslog.syslog(syslog.LOG_DEBUG, "subprocess %d's finished" % process.pid)

class RobotDaemon(daemon.Daemon):
    def __init__(self, *argv, **kwargs):
        super(RobotDaemon, self).__init__(*argv, **kwargs)
        syslog.syslog(syslog.LOG_DEBUG, "%s" % config.path)
        self.hwaddr = get_mac()
        self.ip = subprocess.Popen("ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'", shell=True, stdout=subprocess.PIPE)
        try:
            self.ip = self.ip.stdout.read().split('\n')[0]
            syslog.syslog(syslog.LOG_DEBUG, 'IP address is %s, MAC %s' % (self.ip, self.hwaddr))
        except Exception, e:
            syslog.syslog(syslog.LOG_ERROR, 'Cannot fetch host IP: %s' % e)
        #self.tasks = []

    def reload_config(self):
        #self.clear_tasks()
        try:
            for main_run in Run.objects.filter(hwaddr=None):
                i = 0
                task = main_run.task
                syslog.syslog(syslog.LOG_DEBUG, "%s" % main_run)
                main_run_id = main_run.pk
                my_runs = Run.objects.filter(hwaddr=self.hwaddr, task=task, rerun=False)
                syslog.syslog(syslog.LOG_DEBUG, "my_runs: %s" % my_runs)
                if my_runs:
                    continue
                my_run = Run(task_id=main_run.task.pk, hwaddr=self.hwaddr, ip=self.ip, status=True)
                my_run.save()
                _id = "%s_%04d_%s" % (task.name, my_run.pk, self.ip)
                _cmd = ['python2.7', config.path.pybot, '--pythonpath', "%s:%s" % (config.path.listener_path, config.path.suits_path), '--listener',
                        "%(module)s:%(run_id)s:%(filename)s" % {'module': config.path.listener, 'filename': "listener_" + _id, 'run_id': my_run.pk}]
                _suites = set()
                for test in task.tests.all():
                    _cmd += ['--test', test.name]
                    _suites.add(test.suite.path)
                _outputdir = my_run.path_to_results
                _cmd += ['--outputdir', _outputdir]
                _cmd += _suites
                if not os.path.isdir(_outputdir):
                    os.mkdir(_outputdir)
                #self.tasks.append(Task(self, my_run.pk, on_exit, (_cmd, 0, None, None, subprocess.PIPE, subprocess.PIPE)))
                Task(self, my_run.pk, on_exit, (_cmd, 0, None, None, subprocess.PIPE, subprocess.PIPE))
        except Exception, e:
            syslog.syslog(syslog.LOG_DEBUG, "Cannot fetch tasks: %s, %s" % (e.message, e.args))

#    def clear_tasks(self):
#        map(lambda x: x.finish, self.tasks)
#        self.tasks = []

    def quit(self):
        #self.clear_tasks()
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

