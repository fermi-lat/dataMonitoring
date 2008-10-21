#!/usr/bin/env python

import os
import sys
import ROOT
import time

from pLongTermTrendMaker import *


if __name__ == '__main__':
    MIN_START_TIME = utc2met(convert2sec('Oct/01/2008 00:00:00'))
    MAX_START_TIME = utc2met(convert2sec('Oct/02/2008 00:00:00'))
    MIN_RUN_DURATION = 1000
    RUN_INTENT = 'nomSciOps'
    GROUPS = ['DIGIHIST']

    for group in GROUPS:
        filePath = '%s_reference.txt' % group
        query = pDataCatalogQuery(group, MIN_START_TIME, MAX_START_TIME,
                                  MIN_RUN_DURATION, RUN_INTENT)
        query.dumpList(filePath)

    logFile = file('reference.log', 'w')
    logFile.writelines('Log file created by pRefHistogramsMaker.py on %s.\n' %\
                       time.asctime())
    logFile.writelines('\n')
    logFile.writelines('Selections for histogram merging:\n')
    logFile.writelines('- Start run time between %s and %s (UTC).\n' %\
                       (MIN_START_TIME, MAX_START_TIME))
    logFile.writelines('- Minimum run duration: %s s.\n' % MIN_RUN_DURATION)
    logFile.writelines('- Run intent: "%s".\n' % RUN_INTENT)
    logFile.writelines('- Groups: %s.\n' % GROUPS)
    logFile.writelines('\n')
    logFile.writelines('See the file lists for details. Bye.')
    logFile.close()

    
