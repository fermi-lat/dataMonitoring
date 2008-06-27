#! /usr/bin/env python

import logging
logging.basicConfig(level = logging.DEBUG)

import os
import sys
import time
import ROOT
import math

from lrsProcessor import lrsProcessor


class lrsTkrProcessor(lrsProcessor):

    BRANCHES_LIST    = ['Time:d:(1)',
                        'LrsRateAverage:d:(1)',
                        'LrsRateError:d:(1)'
                        ]

    def process(self):
        self.InputTree.SetBranchStatus('*', 0)
        self.InputTree.SetBranchStatus('Time', 1)
        self.InputTree.SetBranchStatus('LrsAverageRate', 1)
        ROOT.gROOT.SetBatch(1)
        for (tMin, tMax) in self.Bins:
            self.getArray('Time')[0] = (tMax + tMin)/2
            cut = 'Time > %f && Time < %f' % (tMin, tMax)
            self.InputTree.Draw('LrsAverageRate>>h', cut)
            histogram = ROOT.gDirectory.Get('h')
            average = histogram.GetMean()
            error = histogram.GetRMS()
            numEntries = histogram.GetEntries()
            error /= math.sqrt(numEntries)
            self.getArray('LrsRateAverage')[0] = average
            self.getArray('LrsRateError')[0] = error
            histogram.Delete()
            self.fillTree()
        ROOT.gROOT.SetBatch(0)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options]')
    (opts, args) = parser.parse_args()
    processor = lrsTkrProcessor(args[0])
    processor.process()
    processor.close()
