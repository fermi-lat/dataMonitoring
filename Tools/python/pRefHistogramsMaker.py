#!/usr/bin/env python

import os
import sys
import ROOT
import time

from pLongTermTrendMaker import *


if __name__ == '__main__':
    OUTPUT_DIR_PATH = './reference/'
    if not os.path.exists(OUTPUT_DIR_PATH):
        print 'Creating folder %s' % OUTPUT_DIR_PATH
        os.makedirs(OUTPUT_DIR_PATH)
    MIN_START_DATE = 'Dec/01/2009 00:00:00'
    MAX_START_DATE = 'Dec/06/2009 23:59:59'
    MIN_START_TIME = utc2met(convert2sec(MIN_START_DATE))
    MAX_START_TIME = utc2met(convert2sec(MAX_START_DATE))
    MIN_RUN_DURATION = 1000
    RUN_INTENT = 'nomSciOps_diagEna'
    GROUPS = ['DIGIHIST', 'FASTMONHIST', 'RECONHIST', 'MERITHIST']
    for group in GROUPS:
        filePath = '%s_reference.txt' % group
        filePath = os.path.join(OUTPUT_DIR_PATH, filePath)
        query = pDataCatalogQuery(group, MIN_START_TIME, MAX_START_TIME,
                                  MIN_RUN_DURATION, RUN_INTENT)
        query.dumpList(filePath)
        fileList = file(filePath, 'r').readlines()
        rootFilePath = '%s_reference.root' % group
        rootFilePath = os.path.join(OUTPUT_DIR_PATH, rootFilePath)
        cmd = 'hadd  %s' % rootFilePath
        for filePath in fileList:
            cmd += ' %s' % filePath.strip('\n')
        print 'Executing command "%s"...' % cmd
        os.system(cmd)

    logFilePath = os.path.join(OUTPUT_DIR_PATH, 'reference.log')
    logFile = file(logFilePath, 'w')
    logFile.writelines('Log file created by pRefHistogramsMaker.py on %s.\n' %\
                       time.asctime())
    logFile.writelines('\n')
    logFile.writelines('Selections for histogram merging:\n')
    logFile.writelines('- Start run time between %s and %s (UTC).\n' %\
                       (MIN_START_DATE, MAX_START_DATE))
    logFile.writelines('- Minimum run duration: %s s.\n' % MIN_RUN_DURATION)
    logFile.writelines('- Run intent: "%s".\n' % RUN_INTENT)
    logFile.writelines('- Groups: %s.\n' % GROUPS)
    logFile.writelines('\n')
    logFile.writelines('See the file lists for details. Bye.')
    logFile.close()

    
