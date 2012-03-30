from subprocess import Popen, PIPE
from HTMLParser import HTMLParser
from re import sub
from sys import stderr
from traceback import print_exc

class CmdRunner():
    def __init__(self):
        self._error = ''
        self._output = ''
        self._process = None
        self.is_running = False

    def run(self, command, shell=True, pipe=True, do_raise=False):
        self._output = ''
        self._error = ''
        if pipe:
            self._process = Popen(command, shell=shell, stdout=PIPE, stderr=PIPE)
            self._output = self._process.stdout.read().strip()
        else:
            self._process = Popen(command, shell=shell, stderr=PIPE)
        self._error = self._process.stderr.read().strip()
        if do_raise:
            raise Exception(self._error)
  
    def _get_state(self):
        return self._process and self._process.poll() is None
    is_running = property(_get_state) 

    def readout(self):
        if self.is_running:
            return self._process.stdout.readline()

