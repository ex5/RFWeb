#!/usr/bin/env python

import sys
import time
import os
import daemon
import config
from lxml import etree
import subprocess
import threading
import logger
import signal

STATE = {'IDLE': 0, 'RUNNING': 1}

class Task(object):
    def __init__(self, name, on_exit, args):
        self.state = STATE['IDLE']
        # name should be unique otherwise logger will be the same
        self.name = name
        self.on_exit = on_exit
        self.args = args
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
            self.state = STATE['IDLE']
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
    #logger.handlers = []

class RobotDaemon(daemon.Daemon):
    def __init__(self, *argv, **kwargs):
        super(RobotDaemon, self).__init__(*argv, **kwargs)
        self.test_suit_path = config.path.test_suit
        self.logger.debug("path to the test suit: %s" % self.test_suit_path)
        self.tasks = []

    def run_tasks(self, signum, frame):
        self.logger.debug('run_tasks signum: %d, frame: %s' % (signum, frame))
        if not self.tasks:
            self.logger.warning("no tasks available")
        for task in self.tasks:
            if task.state == STATE['IDLE']:
                task.run()
        signal.pause()

    def reload_config(self, signum, frame):
        self.clear_tasks()
        self.logger.error('reload_config signum: %d, frame: %s' % (signum, frame))
        try:
            suits = etree.parse(os.path.abspath(config.path.testlist)).getroot()
            i = 0
            for suit in suits.findall("robot"):
                _cmd = ['pybot', ]
                self.logger.info('found suit: %s' % str(suit.attrib))
                for test in suit.findall("test"):
                    self.logger.info('found test: %s' % str(test.attrib))
                    _cmd += ['--test', test.attrib["name"]]
                _cmd += ['--outputdir', suit.attrib['output'], suit.attrib['suit']] 
                self.logger.info(_cmd)
                if not os.path.isdir(suit.attrib['output']):
                    os.mkdir(suit.attrib['output'])
                self.tasks.append(Task("task_%03d" % i, on_exit, (_cmd, 0, None, None, subprocess.PIPE, subprocess.PIPE)))
                i += 1
        except Exception, e:
            self.logger.error("Cannot open test suit: %s" % str(e))
        signal.pause()

    def clear_tasks(self):
        map(lambda x: x.finish, self.tasks)
        self.tasks = []
        self.logger.debug("task list cleared")

    def quit(self, signum, frame):
        self.logger.error('quit signum: %d, frame: %s' % (signum, frame))
        if not any(map(lambda x: x.state == STATE['RUNNING'], self.tasks)):
            self.clear_tasks()
            self.logger.info('exiting')
            logger.shutdown()
            self.stop()

    def run(self):
        signal.signal(signal.SIGUSR1, self.reload_config)
        signal.signal(signal.SIGUSR2, self.run_tasks)
        signal.signal(signal.SIGQUIT, self.quit)
        signal.pause()

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

