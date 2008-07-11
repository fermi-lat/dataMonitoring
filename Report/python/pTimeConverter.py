
import logging
logging.basicConfig(level = logging.INFO)

import time
import calendar
import types
import sys

# Notes about the time module.
#
# time()
#   Return the time as a floating point number expressed in seconds since the
#   epoch, in UTC
# gmtime([secs])
#   Convert a time expressed in seconds since the epoch to a struct_time in
#   UTC.
# strftime(format[, t])
#   Convert a tuple or struct_time representing a time as returned by gmtime()
#   or localtime() to a string as specified by the format argument.
# strptime(string[, format])
#   Parse a string representing a time according to a format. The return value
#   is a struct_time.

MET_OFFSET = 978307200
FORMAT_STRINGS_DICT = {'Eric Grove'   : '%Y-%j %H:%M:%S',
                       'Max Turri'    : '%d-%b-%Y %H:%M:%S',
                       'M. E. Monzani': '%a %b %d %H:%M:%S UTC %Y',
                       'Luca Baldini' : '%y%j%H%M%S',
                       'Johan Bregeon': '%Y-%j-%Hh%Mm%Ss',
                       'GCN notice'   : '%b/%d/%Y %H:%M:%S'}

def getStringFormat(flavour):
    try:
        return FORMAT_STRINGS_DICT[flavour]
    except:
        sys.exit('Unknown string format flavour "%s".' % flavour)

DEFAULT_FORMAT_STRING = getStringFormat('Eric Grove')

def sec2string(sec, formatString = DEFAULT_FORMAT_STRING):
    return time.strftime(formatString, time.gmtime(sec))

def msec2string(msec, formatString = DEFAULT_FORMAT_STRING):
    return sec2string(msec/1000, formatString)

def string2sec(timestring, formatString = DEFAULT_FORMAT_STRING):
    return calendar.timegm(time.strptime(timestring, formatString))

def string2msec(timestring, formatString = DEFAULT_FORMAT_STRING):
    return 1000*string2sec(timestring, formatString)

def convert2msec(t):
    try:
        logging.info('Trying to convert seconds (UTC into ms)...')
        return int(1000.*float(t))
    except:
        for (key, value) in FORMAT_STRINGS_DICT.items():
            try:
                logging.info('Trying to convert to ms using "%s" format...' %\
                                 key)
                return string2msec(t, value)
            except:
                pass
        sys.exit('Could not convert input time string.')

def convert2sec(t):
    return convert2msec(t)/1000

def availableTimeFormats(sec = 1208563199):
    formats = ''
    for (key, value) in FORMAT_STRINGS_DICT.items():
        formats += '%12s: "%s" (e.g. %s)\n' %\
            (key, value, sec2string(sec, value)) 
    return formats

def met2utc(met):
    return met + MET_OFFSET

def utc2met(utc):
    return utc - MET_OFFSET



if __name__ == '__main__':
    print availableTimeFormats()
    print convert2msec(1208563199)
    print convert2msec('2008-173 02:18:39')
    print convert2msec('2008 173 02:18:39')
