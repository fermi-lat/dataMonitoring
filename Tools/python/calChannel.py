#! /bin/env python

import sys

sys.path.append('../../Common/python')

from pBaseAnalyzer import getCalChannelLocation


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    (opts, args) = parser.parse_args()

    channel = int(args[0])
    print 'Retrieving location for channel %d...' % channel
    print 'Tower = %d, layer = %d, column = %d, face = %d' % getCalChannelLocation(channel)
