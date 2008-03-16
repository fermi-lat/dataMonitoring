#! /bin/env python

import logging
logging.basicConfig(level = logging.DEBUG)

import os
import sys

from pDataBaseBugger import *
from pRootFileBugger import *


class pTrendingTester:
    
    def __init__(self, rootFilePath, runId = None):
        if runId is None:
            runId = self.__getRunId(rootFilePath)
        logging.info('Testing run %d...' % runId)
        self.DataBaseBugger = pTrendingDataBaseBugger(runId)
        self.RootFileBugger = pRootFileBugger(rootFilePath)

    def __getRunId(self, filePath):
        runString = ''
        for character in os.path.basename(filePath):
            if character.isdigit():
                runString += character
        if len(runString) == 10:
            return int(runString)
        else:
            logging.error('Could not extract the runId from %s.' % filePath)
            sys.exit('Abort')

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
        if errorCode:
            logging.error('*** Found errors! ***')
        else:
            logging.info('Got %d points. All ok.' % numPoints)

    def runRandom(self, numTests = 10):
        for i in range(numTests):
            variable = self.RootFileBugger.getRandomBranchName()
            variable = 'Mean_AcdPha_PmtB_AcdTile'
            selection = self.RootFileBugger.getRandomSelection(variable)
            self.run(variable, selection)


if __name__ == '__main__':
    #runId = 258292096
    #rootFilePath = '../trending/chuncks/r0258292096_digiTrend.root'
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] rootFilePath')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    rootFilePath = args[0]
    tester = pTrendingTester(rootFilePath)
    #tester.runRandom()
    tester.run('Digi_Trend_Mean_AcdPha_PmtB_AcdTile', 'acdtile=23')
