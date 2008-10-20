#!/usr/bin/env python

import os
import sys

sys.path.append('../../Report/python')

from pTimeConverter import *

BASE_PATH = '/afs/slac.stanford.edu/u/gl/glast/datacatalog/prod/datacat'
BASE_COMMAND = 'find'
DEFAULT_SITE = 'SLAC_XROOT /Data/Flight/Level1/LPA'
DEFAULT_SORT = 'nRun'


class pDataCatalogQuery:

    def __init__(self, group, minStartTime, maxStartTime = None,
                 minDuration = 1000, intent = 'nomSciOps'):
        self.Command = BASE_PATH
        self.Command += ' %s' % BASE_COMMAND
        self.Command += ' --group %s' % group
        self.Command += ' --site %s' % DEFAULT_SITE
        self.Command += ' --sort %s' % DEFAULT_SORT
        self.Command += ' --filter '
        self.Command += "'"
        self.Command += 'sIntent=="%s"' % intent
        self.Command += ' && nMetStart>%s' % minStartTime
        if maxStartTime is not None:
            self.Command += ' && nMetStart<%s' % maxStartTime
        self.Command += ' && (nMetStop - nMetStart)>%s' % minDuration
        self.Command += "'"

    def dumpList(self, filePath = None):
        cmd = self.Command
        if filePath is not None:
            cmd += ' >> %s' % filePath
        print 'Executing "%s"...' % cmd
        os.system(cmd)
        print 'Done.'


if __name__ == '__main__':
    MIN_START_TIME = utc2met(convert2sec('Sep/04/2008 00:00:00'))
    MAX_START_TIME = None
    GROUP = 'RECONHISTALARMDIST'
    query = pDataCatalogQuery(GROUP, MIN_START_TIME, MAX_START_TIME)
    query.dumpList('test.txt')
