from subprocess import Popen, PIPE
import sys

class CmdRunner(object):
    def __init__(self):
        self._process = None
        self._clear()

    def _clear(self):
        self._error = ''
        self._output = ''

    def _get_state(self):
        return self._process and self._process.poll() is None
    is_running = property(_get_state) 

    def run(self, command, shell=True, pipe=True, do_raise=False):
        self._clear()
        self._process = Popen(command, shell=shell, stdout=pipe and PIPE or None, stderr=PIPE)
        self._output = pipe and self._process.stdout.read().strip() or ''
        self._error = self._process.stderr.read().strip()
        if do_raise and self._error:
            raise Exception(self._error)
  
    def readout(self):
        if self.is_running:
            return self._process.stdout.readline()

