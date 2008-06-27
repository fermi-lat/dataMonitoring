#! /usr/bin/env python

import logging
logging.basicConfig(level = logging.DEBUG)

import os
import sys
import time
import ROOT
import math

from lrsTreeWriter import lrsTreeWriter


class lrsProcessor(lrsTreeWriter):

    INPUT_TREE_NAME  = 'LrsTree'
    OUTPUT_TREE_NAME = 'LrsSummaryTree'

    def __init__(self, inputRootFilePath, binWidth = 10):
        if not os.path.exists(inputRootFilePath):
            sys.exit('Could not find %s. Abort.' % inputRootFilePath)
        self.InputFile = ROOT.TFile(inputRootFilePath)
        self.InputTree = self.InputFile.Get(self.INPUT_TREE_NAME)
        outputRootFilePath = inputRootFilePath.replace('.root', '_summary.root')
        lrsTreeWriter.__init__(self, outputRootFilePath, self.OUTPUT_TREE_NAME,\
                                   self.BRANCHES_LIST)
        self.NumEntries = self.InputTree.GetEntries()
        self.InputTree.GetEntry(0)
        self.StartTime = self.InputTree.Time
        self.InputTree.GetEntry(self.NumEntries - 1)
        self.StopTime = self.InputTree.Time
        logging.info('Data found between %f and %f s.' %\
                         (self.StartTime, self.StopTime))
        numBins = int((self.StopTime - self.StartTime)/binWidth)
        logging.info('Dividing data into %d time intervals...' % numBins)
        self.Bins = [(self.StartTime + i*binWidth,\
                          self.StartTime + (i + 1)*binWidth)\
                         for i in range(numBins)]
        
    def close(self):
        logging.info('Closing files...')
        self.closeTree()
        self.InputFile.Close()


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options]')
    (opts, args) = parser.parse_args()
    processor = lrsProcessor(args[0])
    processor.process()
