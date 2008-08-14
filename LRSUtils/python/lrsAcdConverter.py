#!/usr/bin/env python

import logging
logging.basicConfig(level = logging.DEBUG)

import ROOT
import numpy
import os
import sys

from lrsConverter import lrsConverter

NUM_ACD_TILES = 108


class lrsAcdConverter(lrsConverter):

    _BRANCHES_LIST = ['Time:d:(1)',
                      'CountDuration:d:(1)',
                      'LrsCounts:i:(%d)' % NUM_ACD_TILES,
                      'LrsRate:d:(%d)' % NUM_ACD_TILES,
                      'LrsAverageRate:d:(1)'
                      ]
    DATA_BLOCK_SIZE = 28

    def convert(self):
        logging.info('Converting...')
        while 1:
            timestamp = self.timestamp()
            if timestamp is None:
                break
            for i in range(self.DATA_BLOCK_SIZE - 1):
                averageRate = 0
                line = self.line()
                try:
                    (id, tile1, tile2, cnt1, cnt2, dur) = line.split(',')
                except ValueError:
                    logging.error('Could not parse line %d.' % self.LineNumber)
                    logging.error('Line looks like: "%s".' % line)
                    sys.exit('Abort.')
                (id, tile1, tile2, cnt1, cnt2) =\
                    [int(x) for x in (id, tile1, tile2, cnt1, cnt2)]
                dur = float(dur)
                (rate1, rate2) = (cnt1/dur, cnt2/dur)
                averageRate += rate1
                averageRate += rate2
                self.getArray('Time')[0] = timestamp + i*dur
                self.getArray('LrsCounts')[tile1] = cnt1
                self.getArray('LrsRate')[tile1] = rate1
                self.getArray('LrsCounts')[tile2] = cnt2
                self.getArray('LrsRate')[tile2] = rate2
                self.getArray('CountDuration')[0] = dur
                self.getArray('LrsAverageRate')[0] = averageRate/2.
                self.fillTelemetryInformation(timestamp + i*dur)
                self.fillTree()
        logging.info('Done.')


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options]')
    parser.add_option('-r', '--root-dir', dest = 'r',
                      default = None, type = str,
                      help = 'path to output ROOT folder')
    parser.add_option('-t', '--telemetry-dir', dest = 't',
                      default = None, type = str,
                      help = 'path to output telemetry folder')
    (opts, args) = parser.parse_args()
    converter = lrsAcdConverter(args[0], opts.r, opts.t)
