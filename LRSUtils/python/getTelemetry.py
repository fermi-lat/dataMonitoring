#! /usr/bin/env python

import os
import commands

from telemetryTrendingInterface import telemetryTrendingInterface

LRS_DATA_PATH = '/nfs/farm/g/glast/u42/ISOC-flight/FswDumps/reports/nonEvent/'
DATA_BLOCK_SIZE = {'f1001': 19, 'f1002': 35, 'f1003': 28}
OUTPUT_DIR_PATH = '/nfs/slac/g/glast/users/glground/lbaldini/saa/telemetry/'

filesList = commands.getoutput('ls %s*/f100*' % LRS_DATA_PATH).split('\n')
numFilesLeft = len(filesList)
print '%d files found.' % numFilesLeft

for filePath in filesList:
    numFilesLeft -= 1
    if os.path.getsize(filePath) == 0:
        print '%s is empty.' % filePath
    else:
        for (pattern, blockSize) in DATA_BLOCK_SIZE.items():
            if pattern in filePath:
                interface = telemetryTrendingInterface(filePath,\
                                                       OUTPUT_DIR_PATH,\
                                                       blockSize)
    print '%d files left to look at.' % numFilesLeft

