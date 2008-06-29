#!/usr/bin/env python

import logging
logging.basicConfig(level = logging.DEBUG)

import ROOT
import numpy
import os
import sys

from lrsConverter import lrsConverter


class lrsCalConverter(lrsConverter):

    BRANCHES_LIST = ['Time:d:(1)',
                     'TowerMask:i:(1)',
                     'CounterMask:i:(1)',
                     'CountDuration:d:(2)',
                     'LrsCounts:i:(16, 2)',
                     'LrsRate:d:(16, 2)',
                     'LrsLoAverageRate:d:(1)',
                     'LrsHiAverageRate:d:(1)'
                     ]
    DATA_BLOCK_SIZE = 19

    def convert(self):
        while 1:
            timestamp = self.timestamp()
            if timestamp is None:
                break
            self.getArray('Time')[0] = timestamp
            self.getArray('TowerMask')[0] = int(self.line())
            self.getArray('CounterMask')[0] = int(self.line())
            averageLoRate = 0
            averageHiRate = 0
            for i in range(16):
                (tower, cnt0, cnt1, dur0) = self.line().split(',')
                if int(tower) != i:
                    self.exit('Tower mismatch (expected %d, found %d).' %\
                                  (i, int(tower)))
                (cnt0, cnt1) = [int(x) for x in (cnt0, cnt1)]
                (dur0, dur1) = (float(dur0), float(dur0))
                self.getArray('LrsCounts')[i] = (cnt0, cnt1)
                self.getArray('CountDuration')[:] = (dur0, dur1)
                rates = (cnt0/dur0, cnt1/dur1)
                self.getArray('LrsRate')[i] = rates
                averageLoRate += rates[0]
                averageHiRate += rates[1]
            self.getArray('LrsLoAverageRate')[0] = averageLoRate/16    
            self.getArray('LrsHiAverageRate')[0] = averageHiRate/16
            self.fillTelemetryInformation(timestamp)
            self.fillTree()


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options]')
    (opts, args) = parser.parse_args()
    converter = lrsCalConverter(args[0])
    converter.convert()
    converter.close()
