#!/usr/bin/env python

import logging
logging.basicConfig(level = logging.DEBUG)

import ROOT
import numpy
import os
import sys

from lrsConverter import lrsConverter


NUM_ACD_TILES  = 108
TILE_ID_DICT   = {'Top' : [7, 11, 12, 13, 17],
                  'Long': [42, 60, 70, 96]
                  }
TILE_NUM_DICT  = {}
for (key, value) in TILE_ID_DICT.items():
    TILE_NUM_DICT[key] = len(value)
TILE_AREA_DICT = {'Top' : 1122.0,
                  'Long': 2650.0}


class lrsAcdConverter(lrsConverter):

    _BRANCHES_LIST = ['Time:d:(1)',
                      'TimeSinceSaa:d:(1)',
                      'LrsRate:d:(%d)' % NUM_ACD_TILES
                      ]
    for key in TILE_ID_DICT.keys():
        _BRANCHES_LIST.append('LrsNormRate%s:d:(1)' % key)
        
    DATA_BLOCK_SIZE = 28

    def convert(self):
        logging.info('Converting...')
        done = False
        firstSaaEnterFound = False
        firstSaaExitFound = False
        lastSaaExit = 0
        lastSaaFlag = 0
        while not done:
            for j in range(2):
                if done:
                    break
                timestamp = self.timestamp()
                if timestamp is None:
                    done = True
                else:
                    if j == 1:
                        self.getArray('Time')[0] = timestamp
                        self.fillTelemetryInformation(timestamp)
                        saaFlag = self.getArray('SACFLAGLATINSAA')[0]
                        if saaFlag > 0.5 and not firstSaaEnterFound:
                            logging.info('First SAA enter found at %f s.' %\
                                             timestamp)
                            firstSaaEnterFound = True
                        if firstSaaEnterFound:
                            if saaFlag < 0.5 and lastSaaFlag > 0.5:
                                if not firstSaaExitFound:
                                    logging.info ('Firts SAA exit found.')
                                    firstSaaExitFound = True
                                lastSaaExit = timestamp
                                logging.info('SAA exit found at %f.' %\
                                                 timestamp)
                        lastSaaFlag = saaFlag
                        if not firstSaaExitFound:
                            self.getArray('TimeSinceSaa')[0] = -1
                        else:
                            self.getArray('TimeSinceSaa')[0] = timestamp -\
                                lastSaaExit
                    for i in range(self.DATA_BLOCK_SIZE - 1):
                        (id, tile1, tile2, cnt1, cnt2, dur) =\
                            self.line().split(',')
                        (id, tile1, tile2, cnt1, cnt2) =\
                            [int(x) for x in (id, tile1, tile2, cnt1, cnt2)]
                        dur = float(dur)
                        (rate1, rate2) = (cnt1/dur, cnt2/dur)
                        exp1 = j*NUM_ACD_TILES/2 + i*2
                        exp2 = exp1 + 1
                        if tile1 != exp1:
                            sys.exit('Tile %s expected, got %d.' %\
                                         (exp1, tile1))
                        if tile2 != exp2:
                            sys.exit('Tile %s expected, got %d.' %\
                                         (exp2, tile2))
                        self.getArray('LrsRate')[tile1] = rate1
                        self.getArray('LrsRate')[tile2] = rate2
            for (key, tilesList) in TILE_ID_DICT.items():
                normRate = 0
                varName = 'LrsNormRate%s' % key
                for tile in tilesList:
                    normRate += self.getArray('LrsRate')[tile]
                normRate /= (TILE_NUM_DICT[key]*TILE_AREA_DICT[key])
                self.getArray(varName)[0] = normRate

            #normRateTop = 0
            #for tile in TOP_TILES:
            #    normRateTop += self.getArray('LrsRate')[tile]
            #normRateTop /= (NUM_TOP_TILES*TOP_TILES_AREA)
            #self.getArray('LrsNormRateTop')[0] = normRateTop
            #normRateLong = 0
            #for tile in LONG_TILES:
            #    normRateLong += self.getArray('LrsRate')[tile]
            #normRateLong /= (NUM_LONG_TILES*LONG_TILES_AREA)
            #self.getArray('LrsNormRateLong')[0] = normRateLong
            
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
