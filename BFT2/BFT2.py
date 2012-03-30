#!/usr/bin/env python

import sys
import os
import time
import dialog
import robot
import helpers
import re

colorize= { 
# black, red, green, yellow, blue, magenta, cyan white \Z0-\Z9
        'OK': "\Z2\ZbOK\Zn",
        'FAIL': "\Z1\ZbFAIL\Zn",
        'Error': "\Z1\ZbError\Zn",
        'ERROR': "\Z1\ZBERROR\Zn",
        'PASS': "\Z2\ZbPASS\Zn",
        'ETH1': "\Z2\ZbETH1\Zn",
        'ETH2': "\Z2\ZbETH2\Zn",
        'ETH3': "\Z2\ZbETH3\Zn",
        'ETH4': "\Z2\ZbETH4\Zn",
        }
results = lambda: [x.string for x in map(lambda y: re.match("[\da-eA-E]+_+|PW.*|.*html|.*log|.*out", y), os.listdir('.')) if x]

class BFT2UI(helpers.CmdRunner):
    '''
    Simple UI for BFT2 collections of test cases. Uses on dialog/xdialog
    '''
    def __init__(self, workdir='/opt/BFT2', suit_path="quickstart", head=False):
        super(BFT2UI, self).__init__()
        self._work_dir = os.path.abspath(workdir)
        self._output_dir = None
        os.chdir(self._work_dir)
        self._db_path = self._work_dir + "/BFT2.db"
        self._log_path = '%s/%s.log' % (self._work_dir, time.time())
        self.suit_path = os.path.abspath(suit_path)
        self.dlg = dialog.Dialog(dialog="dialog")
        self.logfile = open(self._log_path, 'w+')
        sys.stderr = self.logfile
        self.log("Logfile open")
        self.ishead = head
        self.flush_state()
        self.dlg.setBackgroundTitle(self.backtitle)
        self.head_IPs = ("192.168.0.253", "192.168.8.253")
        self.display()
   
    def set_buttons(self, btn0='OK', btn1='Cancel', btn2='Exit'):
        self.buttons = [btn0, btn1, btn2]

    def _find_usb_drive(self):
        _attempts = 7
        while not self._output and _attempts:
            self.runcmd('ls /dev/disk/by-id | grep "usb.*part1"')
            if self._error:
                return "ERROR: %s" % self._error
            if not self._output:
                _attempts -= 1
                self.dlg.msgbox("Insert the USB drive then press OK")
                self.show_wait()
                time.sleep(5)
        if not _attempts:
            return "ERROR: couldn't find any USB drives"
        return self._output

    def _get_text_height(self):
        return len(self.text.split('\n')) + 4
    def _set(self, x):
        raise Exception("Property is readonly!")
    height = property(_get_text_height, _set)

    def get_text_width(self):
        return max(sum(map(len, self.buttons)) + 15, max(map(len, self.text.split('\n')))) + 5
    width = property(get_text_width, _set)

    def __str__(self):
        return str([(attr, getattr(self, attr)) for attr in self.__dict__])

    def _reports_to_usb_drive(self, devID):
        _now = time.strftime("%Y_%m_%d-%H-%M-%s")
        _mount_path = "/mnt/usb_%s" % _now
        _device = "/dev/disk/by-id/%s" % devID
        try:
            _f = open('/opt/BFT2/usb.log', 'w+')
            os.mkdir(_mount_path)
            print >> _f, _mount_path
            self.runcmd("mount %s %s" % (_device, _mount_path), do_raise=True)
            self.dlg.infobox(self.text, self.height, self.width)
            _dest_path = _mount_path + "/bft2_%s" % _now
            os.mkdir(_dest_path)
            #self.log(
            print _dest_path, os.path.isdir(_dest_path)
            _gz = '%s/results_%s.tar.gz' % (self._work_dir, time.time())
            _cmd="tar -zcf %s %s/results/ %s" % (_gz, self._work_dir, self._db_path)
            #self.log(
            print >> _f, "Gz", _cmd
            self.runcmd(_cmd)
            _cmd = "cp '%s' '%s'" % (_gz, _dest_path)
            #self.log(
            print >> _f, "Copying: ", _cmd
            self.runcmd(_cmd, do_raise=True)
            #self.log(
            print >> _f, "umount %s" % _mount_path
            self.runcmd("umount %s" % _mount_path, do_raise=True)
            os.rmdir(_mount_path)
        except Exception, e:
            #self.log(
            print >> _f, e, "umount %s" % _mount_path
            self.runcmd("umount %s" % _mount_path, do_raise=True)
            os.rmdir(_mount_path)
            _f.close()
            return "ERROR: %s" % e
        _f.close()
        return 'OK'

    def flush_state(self):
        self.suit = None
        self.text = ""
        self.state = "restart"
        self.title = str(self.__class__).split('.')[1]
        self.backtitle = self.title
        self.buttons = []
        self.chosen_tags = []
        self.dlg.DIALOGRC = ''

    def log(self, *args):
        self.logfile.write(str(time.ctime()) + ', ' + os.path.abspath(os.curdir) + ': ' + str(args) + '\n')

    def quit(self, turn_off_head=False):
        if not self.ishead:
            self.sync_results()
        if 'ERROR' in self.text or 'FAIL' in  self.text:
            self.dlg.msgbox(self.text, self.height, self.width)
        _cmd = "mv %s %s" % (self._log_path, self._output_dir)
        self.log('Moving log', _cmd)
        self.logfile.close()
        self.runcmd(_cmd)
        if turn_off_head:
            '''
            for ip in self.head_IPs:
                self.runcmd("ssh %s 'shutdown -h now'" % ip)
                print >> open('%s/ssh.log' % self._work_dir, 'w+'), self._error, self._output
            '''
            _usb = self._find_usb_drive()
            if not _usb or 'ERROR' in _usb:
                self.dlg.msgbox(_usb and "%s" % _usb or "Cannot write reports")
            else:
                self.text_update("Writing reports to USB-drive.. ", clear=True)
                self.dlg.infobox(self.text, self.height, self.width)
                self.text_update(self._reports_to_usb_drive(_usb))
                self.dlg.infobox(self.text, self.height, self.width)
        self.text_update('Turning off MM')
        self.dlg.infobox(self.text, self.height, self.width)
        self.runcmd('shutdown -h now')
        self.text_update(self._error and "[ERROR] %s" % self._error)
        self.dlg.infobox(self.text, self.height, self.width)
        exit(0)

    def text_update(self, info, clear=False, btn0='OK', btn1='Cancel', btn2='Exit'):
        if clear:
            self.text = ""
        for token in colorize:
            info = info.replace(token, colorize[token])
        self.text += "\n" + info
        if self.state != "restart":
            self.dlg.DIALOGRC = os.path.abspath("%s/.conf/.dialogrc.%s" % (self._work_dir, self.state))

    def show_wait(self):
        return self.dlg.infobox(text='\nPlease wait...\n', height=5, width=25)

    def display(self):
        self.check_pybot()
        self.load_test_suit()
        if not self.suit or not self.pybot or not self.tags:
            self.quit()
        if self.ishead:
            while True:
                self.head_do()
        else:
            while True:
                self.do()
        self.quit()

    def load_test_suit(self):
        if os.path.isdir(self.suit_path):
            return #TODO
        if not os.path.isfile(self.suit_path):
            self.text_update("[FAIL] Could not load test suit")
            return
        try:
            # reading test suite file
            self.suit = robot.parsing.TestData(source=self.suit_path)
            self.tags = {}
            for testcase in self.suit.testcase_table:
                if testcase.tags.value.__class__ == list:
                    for tag in map(str, testcase.tags.value):
                        if tag not in self.tags:
                            self.tags[tag] = []
                        self.tags[tag].append(str(testcase.name))
                else:
                    if str(testcase.tags.value) not in self.tags:
                        self.tags[str(testcase.tags.value)] = []
                    self.tags[str(testcase.tags.value)].append(testcase.name)
        except Exception, e:
            self.log('Load test suit, exception: ', e)
            self.title = colorize["Error"]
            self.text_update("[FAIL] %s is not a valid test suit file" % self.suit_path, widget="msgbox")
            return
        self.text_update("[OK] Test suit %s" % self.suit)

    def check_pybot(self):
        try:
            # checking pybot executable
            self.pybot = dialog._path_to_executable("pybot")
        except Exception:
            self.title = colorize["Error"]
            self.text_update("[FAIL] Could not found pybot executable")
            return
        self.text_update("[OK] pybot executable")

    def head_do(self):
        self.runcmd("pybot --include head %s" % self.suit_path, pipe=False)
        if self._error:
            self.text_update(self._error)
            self.dlg.msgbox(self.text, self.height, self.width)
        self.flush_state()

    def get_UID(self):
        self.UID = None
        for ip in self.head_IPs:
            _cmd = "rsync --timeout=3 -e ssh -avz %(ip)s:%(db)s %(db)s" % {'ip': ip, 'db': self._db_path }

            self.log("Syncing DB", _cmd)
            self.runcmd(_cmd, pipe=True)
            if self._error:
                self.log('rsync: ', self._error, self._output)
                continue
            _cmd = 'sqlite3 %s "SELECT id,trial FROM module WHERE state=1"' % self._db_path
            self.runcmd(_cmd, pipe=True)
            if self._error:
                self.log('sqlite: ', self._error, self._output)
                continue
            self.UID = self._output
            self.log("Current SN", _cmd, self.UID, self._error)
            if self.UID:
                break
        # identify by mac if could not fetch serial number from head
        if not self.UID or self._error:
            self.log("By hwaddr", self.UID, self._error)
            self.runcmd("cat /sys/class/net/eth0/address", pipe=True)
            self.UID = self._output.replace(':','_')
        try:
            self.UID = "%s_%03d" % (self.UID.split('|')[0], int(self.UID.split('|')[1]))
        except Exception:
            self.log('UID', self.UID)
        self.pybot_output = 'output_%s.xml' % self.UID
        self.pybot_log = 'log_%s.html' % self.UID
        self.pybot_report = 'report_%s.html' % self.UID
        return self.UID

    def sync_results(self):
        self.dlg.msgbox('Make sure ETH1 and ETH3 are connected\n')
        self.show_wait()
        time.sleep(3)
        for ip in self.head_IPs:
            _cmd = "rsync --timeout=3 -e ssh -avz %(wd)s/results %(ip)s:%(wd)s" % {'ip': ip, 'wd': self._work_dir}
            self.log("Syncing results", _cmd)
            self.runcmd(_cmd, pipe=True)
            if self._error:
                self.log('rsync: ', self._error, self._output)
            _cmd = "rsync --timeout=3 -e ssh %(db)s %(ip)s:%(db)s" % {'ip': ip, 'db': self._db_path}
            self.log("Syncing DB", _cmd)
            self.runcmd(_cmd, pipe=True)
            if self._error:
                self.log('rsync: ', self._error, self._output)

    def do(self):
        self.set_buttons("OK", "Cancel", "Update")
        _btn = self.dlg.msgbox('Make sure ETH1 and ETH3 are connected.\nPress OK to test\n', help_button=1, help_label=self.buttons[2])
        self.show_wait()
        self._output_dir = "%s/results/%s" % (self._work_dir, self.get_UID())
        if not os.path.isdir(self._output_dir):
            os.makedirs(self._output_dir)
        self.log("Path to write results ", self._output_dir, os.path.isdir(self._output_dir))
        if not self.chosen_tags:
            self.chosen_tags = self.tags.keys()
        if _btn == 5:
            # TODO
            self.dlg.msgbox("Update!")
        elif _btn:
            self.quit()
        os.chdir(self._output_dir)
        _cmd = self.pybot + ' -n noncritical -d %s --exclude head -o %s -l %s -r %s ' % (self._output_dir, self.pybot_output, self.pybot_log, self.pybot_report) + self.suit_path
        self.log("Pybot command: ", _cmd)
        try:
            self.runcmd(_cmd, pipe=False, do_raise=True)
        except Exception, e:
            self.log("!Pybot exception", e)
        from xml.etree import ElementTree
        _test_output = ElementTree.parse(self._output_dir + '/' + self.pybot_output).getroot()
        self.text_update('', clear=True)
        for test in _test_output.findall('*/test'):
            _status = test.find('status').text
            self.log(test, _status)
            if not _status:
                continue # resolution's too low, showing only failed ones
            self.text_update("[%s] \Zb%s\Zn " % (_status and 'FAIL' or 'PASS', test.attrib['name']))
            self.text_update(_status and "%s\n" % _status.replace('\n\n','\n') or '')
        _status = _test_output.find('statistics/total/stat').attrib['fail']
        self.log("Failed tests", _test_output.find('statistics/total/stat').attrib['fail'], _status, int(_status))
        if int(_status) > 0:
           self.state = 'alarm'
        else:
           self.state = 'ok'
        self.text_update('')
        if not self.text or len(self.text) < 5:
            self.text_update("\nAll tests [OK]\n")
        del _test_output
        self.set_buttons("Next", "Finish", "")
        finish = self.dlg.yesno(self.text, self.height, self.width, self.buttons[0], self.buttons[1])
        os.chdir(self._work_dir)
        self.log('Exit', finish and "Saving to USB, turning off head" or "Next")
        if finish:
            self.quit(turn_off_head=True)
        self.flush_state()
        self.quit()

def main():
    if len(sys.argv) > 1:
        print sys.argv
        if '--dir' in sys.argv:
            print os.path.abspath(sys.argv[sys.argv.index('--dir') + 1])
            scheduler = BFT2UI(suit_path=sys.argv[1], head='--head' in sys.argv and True or False, workdir=os.path.abspath(sys.argv[sys.argv.index('--dir') + 1]))
        else:
            scheduler = BFT2UI(suit_path=sys.argv[1], head='--head' in sys.argv and True or False)
    else:
        print "Usage: BFT2.py <path to test suit> [--head]"

if __name__ == "__main__":
    main()

