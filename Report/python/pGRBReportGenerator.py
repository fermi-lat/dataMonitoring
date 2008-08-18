#!/bin/env python

from pReportGenerator import *


class pGRBReportGenerator(pReportGenerator):

    def __init__(self, burstTime, halfWindow, cfgFilePath, outputFilePath):
        startTime = burstTime - halfWindow
        endTime = burstTime + halfWindow
        pReportGenerator.__init__(self, startTime, endTime, cfgFilePath,\
                                  outputFilePath )


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options]')
    parser.add_option('-c', '--config-file', dest = 'c',
                      default = '../xml/grbreport.xml', type = str,
                      help = 'path to the input xml config file')
    parser.add_option('-o', '--output-file', dest = 'o',
                      default = './tex/report.tex', type = str,
                      help = 'path to the output TeX file')
    (opts, args) = parser.parse_args()    
    burstTime = 1208649599000 - 3600*1000*12
    halfWindow = 3600*1000*2
    reportGenerator = pGRBReportGenerator(burstTime, halfWindow, opts.c,\
                                          opts.o)
    reportGenerator.writeReport()
    reportGenerator.compile()    
    
