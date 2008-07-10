
import logging
logging.basicConfig(level = logging.DEBUG)

import os
import sys
import time
import calendar

MET_OFFSET = 978307200
DEFAULT_TIME_FORMAT = '%d-%b-%Y %H:%M:%S'
BRYSON_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
NAVIGATION_TIME_FORMAT = '%Y-%m-%d %H:%M:%S' # 2008-06-25 07:47:21.200000

def met2utc(met):
    return met + MET_OFFSET

def utc2string(utc, stringFormat = BRYSON_TIME_FORMAT):
    return time.strftime(stringFormat, time.gmtime(utc))

def string2utc(timestring, formatString):
    try:
        (sec, msec) = timestring.split('.')
        sec = calendar.timegm(time.strptime(sec, formatString))
        return sec + float('.%s' % msec)
    except:
        return calendar.timegm(time.strptime(timestring, formatString))

def getFileSize(filePath):
    try:
        return os.stat(filePath)[6]
    except OSError:
        return -1

def getFirstTimestamp(filePath):
    fileObject = file(filePath)
    timestamp = met2utc(float(fileObject.readline()))
    fileObject.close()
    return timestamp

def getLastTimestamp(filePath, dataBlockSize):
    fileObject = file(filePath)
    fileSize = getFileSize(filePath)
    numLinesFound = 0
    filePosition = fileSize
    while numLinesFound <= dataBlockSize:
        fileObject.seek(filePosition)
        item = fileObject.read(1)
        if item == '\n':
            numLinesFound += 1
        filePosition -= 1
    timestamp = met2utc(float(fileObject.readline()))
    fileObject.close()
    return timestamp


if __name__ == '__main__':
    print getFirstTimestamp('/data/work/leo/saa/f1001_2360728414034220.csv')
    print getLastTimestamp('/data/work/leo/saa/f1001_2360728414034220.csv', 19)
