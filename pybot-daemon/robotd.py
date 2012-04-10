#!/usr/bin/python2

import sys
import time
import os
import daemon
import config
import subprocess
import threading
import logger
os.environ['DJANGO_SETTINGS_MODULE'] = 'rfweb.settings'
sys.path.append(config.django.app_dir)
from rfweb.rfwebapp.models import Suite, Test, Task, Run, Log

STATE = {'IDLE': 0, 'RUNNING': 1}

class Task(object):
    def __init__(self, parent, name, on_exit, args):
        self.parent = parent
        self.state = STATE['IDLE']
        # name should be unique otherwise logger will be the same
        self.name = name
        self.on_exit = on_exit
        self.args = args
        self.logfile = os.path.join(config.path.logs, "thread_%s.log" % self.name)
        self.logger = logger.get_logger(self.name, os.path.join(config.path.logs, "thread_%s.log" % self.name))
        self.logger.info("task initialized: %s, %s" % (on_exit, args))

    def run(self):
        """
        Runs the given args in a subprocess.Popen, and then calls the function
        on_exit when the subprocess completes.
        on_exit is a callable object, and args is a list/tuple of args that 
        would give to subprocess.Popen.
        """
        def run_in_thread(on_exit, args):
            proc = subprocess.Popen(*args)
            proc.wait()
            on_exit(proc, self.logger)
            self.parent.tasks.remove(self)
            return
        self.thread = threading.Thread(target=run_in_thread, args=(self.on_exit, self.args))
        self.thread.start()
        self.state = STATE['RUNNING']

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
        self.test_suit_path = config.path.test_suit
        self.logger.debug("%s" % config.path)
        self.tasks = []

    def run_tasks(self):
        if not self.tasks:
            self.logger.warning("no tasks available")
        for task in self.tasks:
            if task.state == STATE['IDLE']:
                task.run()

    def reload_config(self):
        self.clear_tasks()
        try:
            for run in Run.objects.filter(running__exact=None):
                task = run.task
                _id = "%s_%04d.log" % (task.name, task.pk)
                _cmd = ['pybot', '--pythonpath', config.path.listener_path]
                _cmd += ['--listener', "%s:%s" % (config.path.listener, "listener_" + _id)]
                self.logger.info('found task: %s' % task.name)
                _suites = set()
                for test in task.tests.all():
                    self.logger.info('found test: %s' % test.name)
                    _cmd += ['--test', test.name]
                    _suites.add(test.suite.path)
                _outputdir = os.path.join(config.path.output, 'task_' + _id)
                _cmd += ['--outputdir', _outputdir]
                _cmd += _suites
                self.logger.info(_cmd)
                if not os.path.isdir(_outputdir):
                    os.mkdir(_outputdir)
                self.tasks.append(Task(self, _id, on_exit, (_cmd, 0, None, None, subprocess.PIPE, subprocess.PIPE)))
        except Exception, e:
            self.logger.error("Cannot fetch tasks: %s" % str(e))

    def clear_tasks(self):
        map(lambda x: x.finish, self.tasks)
        self.tasks = []
        self.logger.debug("task list cleared")

    def quit(self):
        if not any(map(lambda x: x.state == STATE['RUNNING'], self.tasks)):
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
                         logfile=os.path.join(config.path.logs, "robotd.log"),
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
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

if __name__ == "__main__":
    main()

