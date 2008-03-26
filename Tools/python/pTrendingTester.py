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
        pieces = os.path.basename(filePath).split('_')
        for piece in pieces:
            if len(piece) == 11 and piece[0] == 'r':
                try:
                    return int(piece[1:])
                except:
                    pass
        else:
            logging.error('Could not extract the runId from %s.' % filePath)
            sys.exit('Abort')

    def __run(self, variable, selection):
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
                message =  'Point number %d\n' % i
                message += 'DB point  : %s\n'  % dbPoint
                message += 'ROOT point: %s\n'  % rootPoint
                message += 'Difference: %s\n\n'% difference
                print message
                self.LogFile.writelines('%s\n' % message)
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

    def run(self, numTests, quantity, selection, trendType):
        for i in range(numTests):
            if quantity is None:
                q = self.RootFileBugger.getRandomBranchName(trendType)
                if q is None:
                    sys.exit('Could not find branches of type "%s". Abort.' %\
                             trendType)
            else:
                q = quantity
            if selection is None:
                s = self.RootFileBugger.getRandomSelection(q)
            else:
                s = selection
            self.__run('%s%s' % (self.Prefix, q), s)
            


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] rootFilePath')
    parser.add_option('-n', '--num-entries', dest = 'n',
                      default = 1, type = int,
                      help = 'number of queries to the database')
    parser.add_option('-t', '--type', dest = 't',
                      default = None, type = str,
                      help = 'the type of the (random) quantity to be tested')
    parser.add_option('-q', '--quantity', dest = 'q',
                      default = None, type = str,
                      help = 'the trending quantity to be tested')
    parser.add_option('-s', '--selection', dest = 's',
                      default = None, type = str,
                      help = 'the selection on the quantity under test')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    rootFilePath = args[0]
    tester = pTrendingTester(rootFilePath)
    tester.run(opts.n, opts.q, opts.s, opts.t)
