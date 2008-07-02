#! /usr/bin/env python

import os

from telemetryTrendingInterface import telemetryTrendingInterface

LRS_DATA_PATH = '/nfs/farm/g/glast/u42/ISOC-flight/FswDumps/reports/nonEvent/'
DATA_BLOCK_SIZE = {'f1001': 19, 'f1002': 35, 'f1003': 28}
OUTPUT_DIR_PATH = '/nfs/slac/g/glast/users/glground/lbaldini/saa/telemetry/'

filesList = []
for fileName in os.listdir(LRS_DATA_PATH):
    for (pattern, blockSize) in DATA_BLOCK_SIZE.items():
        if pattern in fileName:
            filePath = os.path.join(LRS_DATA_PATH, fileName)
            interface = telemetryTrendingInterface(filePath, OUTPUT_DIR_PATH,\
                                                   blockSize)
            print
            print 
