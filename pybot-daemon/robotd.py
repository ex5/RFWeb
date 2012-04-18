#!/usr/bin/python2.7

import sys
import time
import os
import daemon
import config
import subprocess
import threading
import logger # should be imported _before_ rfweb.settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'rfweb.settings'
sys.path.append(config.django.app_dir)
import rfweb.settings
from rfweb.rfwebapp.models import Suite, Test, Task, Run, Log
from uuid import getnode as get_mac
import datetime
class Task(object):
    def __init__(self, parent, run_id, on_exit, args):
        self.parent = parent
        self.on_exit = on_exit
        self.args = args
        self.run_obj = Run.objects.get(pk=run_id)
        self.logfile = os.path.join(config.path.logs, "task_%s_%s.log" % (hex(self.parent.hwaddr)[2:14], run_id))
        self.logger = logger.get_logger(self.logfile, str(run_id))
        self.logger.info("task initialized: %s, %s" % (on_exit, args))
        # -------- #
        self.my_run = Run(task_id=self.run_obj.task.pk, hwaddr=self.parent.hwaddr, ip=self.parent.ip, status=True)
        self.my_run.save()
        self.run_task()

    def run_task(self):
        """
        Runs the given args in a subprocess.Popen, calls the function on_exit when the subprocess completes.
        on_exit is a callable object;
        args is a list/tuple of args that would be given to subprocess.Popen.
        """
        self.logger.debug('Removed task from parent')
        def run_in_thread(on_exit, args):
            proc = subprocess.Popen(*args)
            proc.wait()
            on_exit(proc, self.logger)
            self.logger.debug('Run TASK!')
            my_run.status = False
            my_run.finish = datetime.datetime.now()
            my_run.save()
            self.parent.tasks.remove(self)
            return
        self.thread = threading.Thread(target=run_in_thread, args=(self.on_exit, self.args))
        self.thread.start()

    def finish(self):
        self.logger.handlers = []
        
def on_exit(process, logger):
    logger.info("\n%s\n" % process.stdout.read())
    logger.info("\n%s\n" % process.stderr.read())
    logger.info("subprocess %d's finished" % process.pid)
    logger.info("LOGGER: %s, HANDLERS: %s" % (str(logger), str(logger.handlers)))

class RobotDaemon(daemon.Daemon):
    def __init__(self, *argv, **kwargs):
        super(RobotDaemon, self).__init__(*argv, **kwargs)
        self.logger.debug("%s" % config.path)
        self.hwaddr = get_mac()
        self.ip = subprocess.Popen("ifconfig  | grep 'inet addr:'| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'", shell=True, stdout=subprocess.PIPE)
        try:
           self.ip = self.ip.stdout.read().split('\n')[0]
           self.logger.debug('IP address is %s, MAC %s' % (self.ip, self.host_id))
        except Exception, e:
            self.logger.error('Cannot fetch host IP: %s' % e)
        self.tasks = []
    def run_tasks(self):
        if not self.tasks:
            self.logger.debug("no tasks available")
            #for task in self.tasks:
            #    task.run_task()
    def reload_config(self):
        self.clear_tasks()
        try:
            for run in Run.objects.filter(hwaddr=None):
                i = 0
                task = run.task
                run_id = run.pk
                my_runs = Run.objects.filter(hwaddr=self.hwaddr, task=task)
                self.logger.debug('My runs: %s' % my_runs)
                if my_runs:
                    self.logger.debug('Already run this task: %s' % task)
                    continue
                _id = "%s_%04d.log" % (task.name, run_id)
                _cmd = ['/usr/bin/python2.7', '/usr/bin/pybot', '--pythonpath', config.path.listener_path, '--listener',
                        "%(module)s:%(run_id)s:%(filename)s" % {'module': config.path.listener, 'filename': "listener_" + _id, 'run_id': run_id}]
                _suites = set()
                for test in task.tests.all():
                    _cmd += ['--test', test.name]
                    _suites.add(test.suite.path)
                _outputdir = os.path.join(rfweb.settings.MEDIA_ROOT, 'run_' + _id)
                _cmd += ['--outputdir', _outputdir]
                _cmd += _suites
                if not os.path.isdir(_outputdir):
                    os.mkdir(_outputdir)
                self.logger.info(_cmd)
                self.tasks.append(Task(self, run_id, on_exit, (_cmd, 0, None, None, subprocess.PIPE, subprocess.PIPE)))
        except Exception, e:
            self.logger.error("Cannot fetch tasks: %s, %s" % (e.message, e.args))
    def clear_tasks(self):
        map(lambda x: x.finish, self.tasks)
        self.tasks = []
        self.logger.debug("task list cleared")
    def quit(self):
        self.clear_tasks()
        self.logger.info('exiting')
        logger.shutdown()
        self.stop()

    def run(self):
        while True:
            time.sleep(2)
            self.reload_config()
            self.run_tasks()
robotd_init = lambda: RobotDaemon(pidfile=config.path.pid_file, 
                         logfile=config.path.stdout,
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

