#!/usr/bin/env python

import sys
import time
import os
import daemon
import robot
import config
from lxml import etree
import subprocess
import threading
import logger

class Task(object):
    def __init__(self, name, on_exit, args):
        # name should be unique otherwise logger will be the same
        self.name = name
        self.on_exit = on_exit
        self.args = args
        self.logger = logger.get_logger(self.name, os.path.join(config.path.logs, "thread_%s.log" % self.name))

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
            return
        self.thread = threading.Thread(target=run_in_thread, args=(self.on_exit, self.args))
        self.thread.start()

def on_exit(process, logger):
    logger.info("\n%s\n" % process.stdout.read())
    logger.info("\n%s\n" % process.stderr.read())
    logger.info("subprocess %d's finished" % process.pid)
    logger.info("LOGGER: %s, HANDLERS: %s" % (str(logger), str(logger.handlers)))
    logger.handlers = []

class RobotDaemon(daemon.Daemon):
    def run_tasks(self):
        for task in self.tasks:
            task.run()
        self.clear_tasks()

    def clear_tasks(self):
        self.tasks = []

    def run(self):
        self.test_suit_path = config.path.test_suit
        self.logger.debug("path to the test suit: %s" % self.test_suit_path)
        self.clear_tasks()
        while True:
            if self.tasks: 
                self.run_tasks()
            time.sleep(1)
            if not os.path.isfile(config.path.start_flag):
                continue
            try:
                os.remove(config.path.start_flag)
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

if __name__ == "__main__":
    robotd = RobotDaemon(pidfile=config.path.pid_file, 
                         logfile=os.path.join(config.path.logs, "robotd.log"),
                         stdout=config.path.stdout, 
                         stderr=config.path.stderr)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            robotd.start()
        elif 'stop' == sys.argv[1]:
            robotd.stop()
        elif 'restart' == sys.argv[1]:
            robotd.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
