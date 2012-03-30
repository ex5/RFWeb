#!/usr/bin/env python

import sys
import os
import subprocess
import time
import dialog
import robot

colorize= { 
# black, red, green, yellow, blue, magenta, cyan white \Z0-\Z9
        'OK': "\Z2\ZbOK\Zn",
        'FAIL': "\Z1\ZbFAIL\Zn",
        'Error': "\Z1\ZbError\Zn",
        'ERROR': "\Z1\ZBERROR\Zn",
        'PASS': "\Z2\ZbPASS\Zn",
        }

class TestScheduler():
    '''
    Simple test scheduler with UI based on dialog/xdialog
    '''
    def __init__(self, logfile="dscheduler.log", suit_path="quickstart"):
        self.logfile = open(logfile, 'w')
        self.suit_path = suit_path
        self.dlg = dialog.Dialog(dialog="dialog")
        self.flush_state()
        self.dlg.setBackgroundTitle(self.backtitle)
        self.display()

    def get_info_height(self):
        return len(self.text.split('\n')) + 5
    height = property(get_info_height)

    def get_info_width(self):
        return max(map(len, self.text.split('\n'))) + 5
    width = property(get_info_width)

    def __str__(self):
        return str([(attr, getattr(self, attr)) for attr in self.__dict__])

    def flush_state(self):
        self.suit = None
        self.text = ""
        self.state = "restart"
        self.title = str(self.__class__).split('.')[1]
        self.backtitle = self.title
        self.dlg.DIALOGRC = ''

    def log(self, *args):
        self.logfile.write(str(time.ctime()) + ': ' + str(args) + '\n')

    def quit(self):
        self.text_update(" Bye! ", clear=True)
        self.dlg.infobox(self.text, self.height, self.width)
        self.log("quit", self)
        self.logfile.close()
        exit(0)

    def text_update(self, info, widget="infobox", clear=False):
        if clear:
            self.text = ""
        for token in colorize:
            info = info.replace(token, colorize[token])
        self.text += "\n" + info
        if self.state != "restart":
            self.dlg.DIALOGRC = os.path.abspath(".dialogrc.%s" % self.state)

    def draw_menu(self):
        height = len(self.text[1]) + 7
        width = max(max(max(map(lambda x: len(x[1]), self.text[1])), len(self.text[0])), len(self.title)) + 5
        return self.dlg.menu(text=self.text[0], height=height, width=width, menu_height=7, choices=self.text[1])

    def draw_checklist(self):
        height = len(self.text[1]) + 7
        width = max(max(max(map(lambda x: len(x[0]), self.text[1])), len(self.text[0])), len(self.title)) + 12
        return self.dlg.checklist(text=self.text[0], height=height, width=width, list_height=7, choices=self.text[1])

    def display(self):
        while self.state != "exit":
            if self.state == "restart":
                self.do()
        self.dlg.msgbox(self.text, self.height, self.width)
        self.quit()

    def load_test_suit(self):
        if os.path.isdir(self.suit_path):
            return #TODO
        if not os.path.isfile(self.suit_path):
            self.text_update("[FAIL] Could not load test suit")
            return
        # reading test suite file
        try:
            self.suit = robot.parsing.TestData(source=self.suit_path)
        except Exception:
            self.title = colorize["Error"]
            self.text_update("[FAIL] %s is not a valid test suit file" % self.suit_path, widget="msgbox")
            return
        self.text_update("[OK] Test suit %s" % self.suit)

    def check_pybot(self):
        # checking pybot executable
        try:
            self.pybot = dialog._path_to_executable("pybot")
        except Exception:
            self.title = colorize["Error"]
            self.text_update("[FAIL] Could not found pybot executable")
            return
        self.text_update("[OK] pybot executable")

    def do(self):
        self.check_pybot()
        self.load_test_suit()
        if not self.suit or not self.pybot:
            self.state = "exit"
            return
        keywords = map(lambda x: (str(x.name), "", 1), self.suit.keywords)
        self.log(self.suit, keywords)
        if keywords:
            self.text = ["Please, choose tests:", keywords]
            chosen = self.draw_checklist()
            self.log(chosen)
        exit = self.dlg.yesno(self.text + "\nProceed?\n", len(self.text.split('\n')) + 5, max(map(len, self.text.split('\n'))) + 5)
        if exit:
            self.state = "exit"
            return
        testrun = subprocess.Popen([self.pybot, self.suit_path], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        self.text_update("", clear=True)
        while testrun.poll() is None:
            line = testrun.stdout.readline()
            if '|' in line or ',' in line:
                if 'FAIL' in line:
                    self.state = "alarm"
                self.text_update(line)
                self.dlg.infobox(self.text, self.height, self.width)
        exit = self.dlg.yesno(self.text, self.height, self.width)
        if exit:
            self.state = "exit"
        else:
            self.flush_state()

def main():
    if len(sys.argv) > 1:
        print sys.argv
        scheduler = TestScheduler(suit_path=sys.argv[1])

if __name__ == "__main__":
    main()
