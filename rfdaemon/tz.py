#!/usr/bin/python2.7

from datetime import tzinfo, timedelta, datetime

class tz(tzinfo):
    def __init__(self, offset=0):
        self.offset = int(offset)
        self.offset_days = self.offset / 24.

    def dst(self, dt):
        return timedelta(0)

    def utcoffset(self, dt=None):
        return timedelta(self.offset_days)

    def tzname(self):
        return "%s%02d:00" % (self.offset >= 0 and '+' or '', self.offset)
