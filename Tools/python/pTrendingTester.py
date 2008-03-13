#! /bin/env python

import logging
logging.basicConfig(level = logging.DEBUG)

from pDataBaseBugger import *
from pRootFileBugger import *


class pTrendingTester:
    
    def __init__(self, runId, rootFilePath):
        runId = int(runId)
        logging.info('Testing run %d...' % runId)
        self.DataBaseBugger = pTrendingDataBaseBugger(runId)
        self.RootFileBugger = pRootFileBugger(rootFilePath)

    def run(self, variable, selection):
        errorCode = False
        logging.info('Running on variable %s, selection %s...' %\
                         (variable, selection))
        dbDataPoints = self.DataBaseBugger.getDataPoints(variable, selection)
        rootDataPoints = self.RootFileBugger.getDataPoints(variable, selection)
        dbNumPoints = len(dbDataPoints)
        rootNumPoints = len(rootDataPoints)
        numPoints = min(dbNumPoints, rootNumPoints)
        if (dbNumPoints != rootNumPoints):
            logging.error('Got %d points from db, %d from root file.' %\
                              (dbNumPoints, rootNumPoints))
            errorCode = True
        for i in range(dbNumPoints):
            dbPoint = dbDataPoints[i]
            rootPoint = rootDataPoints[i]
            difference = dbPoint - rootPoint
            if not (difference.isNull()):
                print dbPoint, rootPoint, difference
                errorCode = True
        if not errorCode:
            logging.info('Got %d points. All ok.' % numPoints)



if __name__ == '__main__':
    #runId = 258292096
    #rootFilePath = '../trending/chuncks/r0258292096_digiTrend.root'
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] runId rootFilePath')
    (opts, args) = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
        parser.error('Exactly two argument required.')
    (runId, rootFilePath) = args
    tester = pTrendingTester(runId, rootFilePath)
    if tester.run('Digi_Trend_Mean_AcdPha_PmtB_AcdTile', 'acdtile=23'):
        print '*** Error(s) found. ***'
