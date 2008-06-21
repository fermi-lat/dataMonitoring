
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

EG_FORMAT_STRING  = '%Y-%j %H:%M:%S'    #2008-173 02:18:39
MAX_FORMAT_STRING = '%d-%b-%Y %H:%M:%S' #21-Jun-2008 00:50:40


def sec2string(sec, formatString = EG_FORMAT_STRING):
    return time.strftime(formatString, time.gmtime(sec))

def msec2string(msec, formatString = EG_FORMAT_STRING):
    return sec2string(msec/1000, formatString)

def string2sec(timestring, formatString = MAX_FORMAT_STRING):
    return calendar.timegm(time.strptime(timestring, formatString))

def string2msec(timestring, formatString = MAX_FORMAT_STRING):
    return 1000*string2sec(timestring, formatString)

def convert2msec(t):
    if type(t) == types.FloatType:
        t = int(t)
    if type(t) == types.IntType:
        return 1000*t
    elif type(t) == types.StringType:
        try:
            return string2msec(t, EG_FORMAT_STRING)
        except:
            try:
                return string2msec(t, MAX_FORMAT_STRING)
            except:
                sys.exit('Could not convert input time string.')



if __name__ == '__main__':
    print sec2string(1214009440)             # 21 Jun 2008 00:50:40
    print string2sec('21 Jun 2008 00:50:40') # 1214009440
    print sec2string(1208563199)             # 18 Apr 2008 23:59:59
    print string2sec('18 Apr 2008 23:59:59') # 1208563199
    print convert2msec(1208563199)
    print convert2msec('2008-173 02:18:39')
