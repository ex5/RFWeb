#!/usr/bin/env python

import sys
import time
import os
from daemon import Daemon
import robot
import config
from lxml import etree
import subprocess

class RobotDaemon(Daemon):
    def run(self):
        self.test_suit_path = config.path.test_suit
        self.logger.debug("path to the test suit: %s" % self.test_suit_path)
        self.subprocesses = []
        while True:
            time.sleep(1)
            if self.subprocesses:
                to_remove = []
                for process in self.subprocesses:
                    if process.poll():
                        to_remove.append(process)
                        self.logger.info(process.stdout.read())
                        self.logger.info(process.stderr.read())
                        self.logger.info("subprocess %d's finished" % process.pid)
                self.subprocesses = filter(lambda x: x not in to_remove, self.subprocesses)
            if not os.path.isfile(config.path.start_flag):
                continue
            try:
                os.remove(config.path.start_flag)
                suits = etree.parse(os.path.abspath(config.path.testlist)).getroot()
                for suit in suits.findall("robot"):
                    _cmd = ['pybot', ]
                    self.logger.info('found suit: %s' % str(suit.attrib))
                    for test in suit.findall("test"):
                        self.logger.info('found test: %s' % str(test.attrib))
                        _cmd += ['--test', test.attrib["name"]]
                    _cmd += ['--outputdir', suit.attrib['output'], suit.attrib['suit']] 
                    self.logger.info(_cmd)
                    self.subprocesses.append(subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
                    self.logger.debug('subprocesses %s' % str(map(lambda x: x.pid, self.subprocesses)))
            except Exception, e:
                self.logger.error("Cannot open test suit: %s" % str(e))

if __name__ == "__main__":
    daemon = RobotDaemon(pidfile=config.path.pid_file, 
                         logfile=config.path.log_file, 
                         stdout=config.path.stdout, 
                         stderr=config.path.stderr)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
