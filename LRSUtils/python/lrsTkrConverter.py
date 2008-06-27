#!/usr/bin/env python

import logging
logging.basicConfig(level = logging.DEBUG)

import ROOT
import numpy
import os
import sys


from lrsConverter import lrsConverter


class lrsTkrConverter(lrsConverter):

    BRANCHES_LIST = ['Time:d:(1)',
                     'TowerMask:i:(1)',
                     'CounterMask:i:(1)',
                     'CountDuration:d:(4)',
                     'LrsCounts:i:(16, 4)',
                     'LrsRate:d:(16, 4)',
                     'LrsAverageRate:d:(1)'
                     ]
    DATA_BLOCK_SIZE = 35

    def convert(self):
        while 1:
            timestamp = self.timestamp()
            if timestamp is None:
                break
            self.getArray('Time')[0] = timestamp
            self.getArray('TowerMask')[0] = int(self.line())
            self.getArray('CounterMask')[0] = int(self.line())
            averageRate = 0
            for i in range(16):
                (tower, cnt0, cnt1, dur0) = self.line().split(',')
                if int(tower) != i:
                    self.exit('Tower mismatch (expected %d, found %d).' %\
                                  (i, int(tower)))
                (tower, cnt2, cnt3, dur2) = self.line().split(',')
                if int(tower) != i:
                    self.exit('Tower mismatch (expected %d, found %d).' %\
                                  (i, int(tower)))
                (cnt0, cnt1, cnt2, cnt3) =\
                    [int(x) for x in (cnt0, cnt1, cnt2, cnt3)]
                (dur0, dur2) = [float(x) for x in (dur0, dur2)]
                (dur1, dur3) = (dur0, dur2)
                self.getArray('LrsCounts')[i] = (cnt0, cnt1, cnt2, cnt3)
                self.getArray('CountDuration')[:] = (dur0, dur1, dur2, dur3)
                rates = (cnt0/dur0, cnt1/dur1, cnt2/dur2, cnt3/dur3)
                self.getArray('LrsRate')[i] = rates
                averageRate += sum(rates)
            self.getArray('LrsAverageRate')[0] = averageRate/64
            self.fillTree()


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options]')
    (opts, args) = parser.parse_args()
    converter = lrsTkrConverter(args[0])
    converter.convert()
    converter.close()
