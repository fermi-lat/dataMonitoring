#! /bin/env python

import logging
logging.basicConfig(level = logging.DEBUG)

import os
import sys
import time

from pDataBaseBugger import *
from pRootFileBugger import *


class pTrendingTester:
    
    def __init__(self, rootFilePath, runId = None):
        if runId is None:
            runId = self.__getRunId(rootFilePath)
        logging.info('Testing run %d...' % runId)
        self.DataBaseBugger = pTrendingDataBaseBugger(runId)
        self.RootFileBugger = pRootFileBugger(rootFilePath)
        self.Prefix = self.RootFileBugger.Prefix
        logFileName = '%s.log' % time.asctime().replace(' ', '_')
        logFilePath = os.path.join('..', 'log', logFileName)
        self.LogFile = file(logFilePath, 'w')

    def __del__(self):
        try:
            self.LogFile.close()
        except:
            pass

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
        numErrors = 0
        message = 'Running on "%s", selection: "%s"...' % (variable, selection)
        logging.debug(self.RootFileBugger.getBranchInfo(variable))
        logging.info(message)
        self.LogFile.writelines('%s\n' % message)
        dbDataPoints = self.DataBaseBugger.getDataPoints(variable, selection)
        rootDataPoints = self.RootFileBugger.getDataPoints(variable, selection)
        dbNumPoints = len(dbDataPoints)
        rootNumPoints = len(rootDataPoints)
        numPoints = min(dbNumPoints, rootNumPoints)
        if (dbNumPoints != rootNumPoints):
            logging.error('Got %d points from db, %d from root file.' %\
                              (dbNumPoints, rootNumPoints))
        for i in range(dbNumPoints):
            dbPoint = dbDataPoints[i]
            rootPoint = rootDataPoints[i]
            difference = dbPoint - rootPoint
            if not (difference.isNull()):
                print 'Point number %d' % i
                print 'DB point  : ', dbPoint
                print 'ROOT point: ', rootPoint
                print 'Difference: ', difference
                print
                numErrors += 1
        if numErrors:
            message = 'Found %d errors (%d points) in "%s", selection "%s"!' %\
                      (numErrors, numPoints, variable, selection)
            logging.error(message)
            self.LogFile.writelines('%s\n' % message)
        else:
            message = 'Got %d points. All ok.' % numPoints
            logging.info(message)
            self.LogFile.writelines('%s\n' % message)

    def runRandom(self, numTests = 10):
        for i in range(numTests):
            variable = self.RootFileBugger.getRandomBranchName()
            selection = self.RootFileBugger.getRandomSelection(variable)
            self.run('%s%s' % (self.Prefix, variable), selection)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] rootFilePath')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    rootFilePath = args[0]
    tester = pTrendingTester(rootFilePath)
    tester.runRandom(1)
