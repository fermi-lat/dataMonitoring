#!/bin/env python

import sys

from pReportGenerator import *
from pTimeConverter   import *

logging.basicConfig(level = logging.INFO)


DEFAULT_CFG_FILE_PATH = os.path.join(BASE_DIR_PATH, '../xml/grbReport.xml')


class pGRBReportGenerator(pReportGenerator):

    def __init__(self, burstTime, halfWindow, pdfFolderPath, cfgFilePath):
        endTime = burstTime + int(halfWindow*3600000)
        pReportGenerator.__init__(self, endTime, 2*halfWindow, pdfFolderPath,\
                                      cfgFilePath)


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options]')
    parser.add_option('-c', '--config-file', dest = 'c',
                      default = DEFAULT_CFG_FILE_PATH, type = str,
                      help = 'path to the input xml config file')
    parser.add_option('-d', '--dir-path', dest = 'd',
                      default = './report', type = str,
                      help = 'path to the folder for the output pdf file')
    parser.add_option('-b', '--burst-time', dest = 'b',
                      default = None,
                      help = 'the burts time (in s or as a string)')
    parser.add_option('-s', '--half-window', dest = 's',
                      default = 2, type = int,
                      help = 'the report half time span (in hours)')
    parser.add_option('-t', '--time-formats',
                      action='store_true', dest='t', default=False,
                      help='print the list of avilable time formats and exit')
    parser.add_option('-l', '--do-not-cleanup-LaTeX',
                      action='store_false', dest='l', default=True,
                      help='do not clean up the temporary LaTeX folder')
    (opts, args) = parser.parse_args()
    if opts.t:
        print 'Available format strings for specifying end time:\n%s' %\
            availableTimeFormats()
        sys.exit()
    if opts.b is None:
        sys.exit('Please provide the burst time.')
    burstTime = convert2msec(opts.b)
    reportGenerator = pGRBReportGenerator(burstTime, opts.s, opts.d, opts.c)
    reportGenerator.writeReport()
    reportGenerator.compile()    
    reportGenerator.copyPdfAndCleanUp(opts.l)
