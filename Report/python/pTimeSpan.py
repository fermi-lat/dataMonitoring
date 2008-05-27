import os
import logging
import sys
import time

logging.basicConfig(level = logging.DEBUG)


INPUT_FORMAT_STRING = '%b/%d/%Y %H:%M:%S'


class pTimeSpan:

    def __init__(self, string):
        try:
            (label, self.TimeString) = string.split(' : ')
            self.TimeString = self.TimeString.strip()
            (startString, endString) = self.TimeString.split('-')
            self.StartTime = time.strptime(startString, INPUT_FORMAT_STRING)
            self.EndTime = time.strptime(endString, INPUT_FORMAT_STRING)
        except:
            logging.error('Unexpected time string format: "%s"' % string)
            self.TimeString = string

    def getFormattedTimeSpan(self, formatString):
        return '%s -- %s' % (time.strftime(formatString, self.StartTime),\
                             time.strftime(formatString, self.EndTime))

    def getEricGroveTimeSpan(self):
        return self.getFormattedTimeSpan('%Y-%j %H:%M:%S')



if __name__ == '__main__':
    tstr = 'Time Interval (UTC) :  Apr/19/2008 00:00:00-Apr/19/2008 23:59:59'
    timeSpan = pTimeSpan(tstr)
    print timeSpan.getEricGroveTimeSpan()
