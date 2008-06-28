
import logging
logging.basicConfig(level = logging.DEBUG)

import os
import sys
import time

MET_OFFSET = 978307200
DEFAULT_TIME_FORMAT = '%d-%b-%Y %H:%M:%S'
BRYSON_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

def met2utc(met):
    return met + MET_OFFSET

def utc2string(utc, stringFormat = BRYSON_TIME_FORMAT):
    return time.strftime(stringFormat, time.gmtime(utc))

def getFirstTimestamp(filePath):
    fileObject = file(filePath)
    timestamp = met2utc(float(fileObject.readline()))
    fileObject.close()
    return timestamp

def getLastTimestamp(filePath, dataBlockSize):
    fileObject = file(filePath)
    fileSize = os.stat(filePath)[6]
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
