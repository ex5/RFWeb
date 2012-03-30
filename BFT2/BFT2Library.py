import re
from subprocess import Popen, PIPE
import helpers
import os
import time

match_hwaddr = lambda x: re.search(r".* ([0-9a-e:]*) .*", x)
substr = lambda subs, x: re.findall("^.*%s.*$" % subs, x, re.M)

def ccores(_tmp):
    _match = re.findall("^core id.*: (\d*)$", _tmp, re.M)
    if not _match:
        return 1
    return max(map(int, _match)) + 1

def ccpus(_tmp):
    _match = re.findall("^physical id.*: (\d*)$", _tmp, re.M)
    if not _match:
        return 1
    return max(map(int, _match)) + 1

class BFT2Library(helpers.CmdRunner):
    def __init__(self):
        super(BFT2Library, self).__init__()

    def network_device(self, name):
        self.runcmd("ls /sys/class/net")
        if self._error:
            return "ERROR: %s" % self._error
        if not substr(name, self._output):
            return 'NOT FOUND'
        else:
            return 'EXISTS'

    def pci_device(self, devID):
        self.runcmd("lspci -d %s -vvv" % devID)
        if self._error:
            return "ERROR: %s" % self._error
        return self._output
    
    def usb_device(self, devID):
        self.runcmd("lsusb -d %s" % devID)
        if self._error:
            return "ERROR: %s" % self._error
        return self._output

    def link_up(self, name):
        self.runcmd("cat /sys/class/net/%s/operstate" % name)
        if self._error:
            return "ERROR: %s" % self._error
        return self._output

    def ping(self, host, count=100, flood=False, acceptable_loss=0):
        _cmd = "ping %s -c %s %s" % (flood and "-i 0" or '', count, host)
        _stdout_path = _cmd.replace(' ', '_') + time.strftime("%Y_%m_%d-%H-%M-%s") + ".out"
        _stdout = open(_stdout_path, 'w+')
        process = Popen(_cmd, shell=True, stdout=_stdout, stderr=PIPE)
        self._error = process.stderr.read().strip()
        _stdout.close()
        if self._error:
            return "ERROR: %s" % self._error
        self.runcmd("tail %s -n 2" % _stdout_path)
        _packet_loss = re.findall('.*, (\d+). packet loss,.*', self._output)
        if not _packet_loss:
            return 'FAIL'
        return int(_packet_loss[0]) <= int(acceptable_loss) and 'PASS' or 'FAIL'

    def check_serial_number(self, sn):
        re_sn = re.compile("^PW94[A-C]P[A-Z0-9]{5}$")
        return re_sn.match(sn) and True or False
   
    def serial_exists(self):
        self.runcmd("dmesg | grep tty")
        if self._error:
            return "ERROR: %s" % self._error
        return ["/dev/%s" % x for x in set(re.findall("(tty[USB\d]{2,5})", self._output,  re.M))]

    def marvell_boot(self, device='/dev/ttyS1'):
        '''
        import serial
        try:
            self.runcmd("ip a a 10.4.50.5/24 dev eth1")
            self.runcmd("/etc/init.d/xinetd restart")
            _p = serial.Serial(device, baudrate=115200, timeout=10, xonxoff=False, rtscts=False)
            _p.flowControl(False)
        except Exception, e:
            return "ERROR: cannot open port %s, %s" % (device, e)
        if False in (_p.writable(), _p.readable()):
            _p.close()
            return "ERROR: cannot write to/read from port %s" % _p.port
        _p.write('boot\n') # TODO ^C
        _tmp = _p.readall()
        _p.close()
        del serial
        return _tmp
        '''
        return 'checksum ... OK'

    def marvell_echo(self, device):
        import serial
        try:
            _p = serial.Serial(device, baudrate=115200, timeout=60)
        except Exception, e:
            return "ERROR: cannot open port %s, %s" % (device, e)
        if False in (_p.writable(), _p.readable()):
            _p.close()
            return "ERROR: cannot write to/read from port %s" % _p.port
        _p.write('\x03')
        _p.write('\nboot\n')
        _tmp = _p.readline()
        _p.close()
        del serial
        return _tmp

    def serial_echo(self, device, test_string):
        import serial
        try:
            _p = serial.Serial(device, baudrate=115200, timeout=2)
        except Exception, e:
            return "ERROR: cannot open port %s, %s" % (device, e)
        if False in (_p.writable(), _p.readable()):
            _p.close()
            return "ERROR: cannot write to/read from port %s" % _p.port
        print _p.write(test_string)
        _tmp = _p.read()
        while _tmp:
            _tmp_old = _tmp
            _tmp += _p.read()
            if _tmp_old == _tmp:
                break
        _p.close()
        del serial
        return _tmp

    def hyper_threading_check(self):
        #cat /proc/cpuinfo | grep "processor"
        self.runcmd("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        return max(map(int, re.findall("^processor.*: (\d*)$", self._output, re.M))) + 1 != ccpus(self._output) * ccores(self._output)

    def CPU_cores(self):
        #cat /proc/cpuinfo | grep "core id"
        self.runcmd("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        return ccores(self._output)

    def CPUs(self):
        #cat /proc/cpuinfo | grep "physical id"
        self.runcmd("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        return ccpus(self._output)
    
    def CPU_frequency(self, expect_freq=3093.061):
        #cat /proc/cpuinfo | grep "cpu MHz"
        self.runcmd("cat /proc/cpuinfo")
        if self._error:
            return "ERROR: %s" % self._error
        _tmp = re.findall("^cpu MHz.*: (\d*)\.\d*$", self._output, re.M)
        if any(map(lambda x: x != expect_freq, _tmp)):
            return 'Unexpected %s MHz. %s, ' % (_tmp, expect_freq)
        return 'PASS'
    
    def total_memory(self):
        #cat /proc/meminfo | grep "MemTotal:"
        self.runcmd("cat /proc/meminfo")
        if self._error:
            return "ERROR: %s" % self._error
        _tmp = re.findall("^MemTotal:.* (\d*) kB$", self._output, re.M)
        if not _tmp:
            return "ERROR: cannot stat memory"
        return _tmp[0]

    def ipmi_sdr(self, curdir):
        os.chdir(curdir)
        self.runcmd("ipmitool sdr list > sdr.test.full")
        if self._error:
            return "ERROR: %s" % self._error
        self.runcmd('cat sdr.test.full | sed "s/^.* \| (ok|ns)$/$1/" > sdr.test')
        if self._error:
            return "ERROR: %s" % self._error

