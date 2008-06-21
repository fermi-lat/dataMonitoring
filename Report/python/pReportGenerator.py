#!/bin/env python

import os
import logging
import re
import sys

logging.basicConfig(level = logging.INFO)

from pLaTeXWriter     import pLaTeXWriter
from pReportPanel     import pReportPanel
from pReportPage      import pReportPage
from pDownloadManager import pDownloadManager
from pXmlElement      import pXmlElement
from xml.dom          import minidom
from pTimeConverter   import *


LOGO_IMAGE_NAME = 'glastLogo.png'
PREAMBLE_NAME = 'preamble.tex'
    

class pReportGenerator(pLaTeXWriter, pDownloadManager):
    
    def __init__(self, startTime, endTime, cfgFilePath, outputFilePath):
        pDownloadManager.__init__(self)
        pLaTeXWriter.__init__(self, outputFilePath)
        self.StartTime = startTime
        self.EndTime = endTime
        self.TimeSpan = '%s -- %s' %\
            (msec2string(self.StartTime), msec2string(self.EndTime))
        self.XmlBaseElement = pXmlElement(minidom.parse(file(cfgFilePath)))
        self.PagesList = []
        self.PanelsDict = {}
        self.parseConfiguration()
        self.invalidateSession()

    def parseConfiguration(self):
        reportTag = self.XmlBaseElement.getElementByTagName('report')
        self.Title = reportTag.getAttribute('title', '')
        for pageTag in reportTag.getElementsByTagName('page'):
            if pageTag.evalAttribute('enabled'):
                page = pReportPage()
                for panelTag in pageTag.getElementsByTagName('panel'):
                    if panelTag.evalAttribute('enabled'):
                        panelName = panelTag.getAttribute('name')
                        if panelName not in self.PanelsDict.keys():
                            panel = pReportPanel(panelName, self.StartTime,\
                             self.EndTime, reportFolder = self.LaTexFolderPath)
                            self.PanelsDict[panelName] = panel
                        else:
                            logging.info('Panel %s already downloaded.' %\
                                         panelName)
                            panel = self.PanelsDict[panelName]
                        page.addPanel(panel)
                self.PagesList.append(page)

    def writeReport(self):
        self.writeHeader()
        logging.info('Copying the GLAST logo into the report folder...')
        os.system('cp %s %s' % (LOGO_IMAGE_NAME, self.LaTexFolderPath))
        logging.info('Copying the TeX preamble into the report folder...')
        os.system('cp %s %s' % (PREAMBLE_NAME, self.LaTexFolderPath))
        for page in self.PagesList:
            self.addPage(page, self.TimeSpan)
        self.writeTrailer()
 

if __name__ == '__main__':
    import time
    utcmsec = int(1000*time.time())
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options]')
    parser.add_option('-c', '--config-file', dest = 'c',
                      default = '../xml/mainreport.xml', type = str,
                      help = 'path to the input xml config file')
    parser.add_option('-o', '--output-file', dest = 'o',
                      default = './tex/report.tex', type = str,
                      help = 'path to the output TeX file')
    parser.add_option('-e', '--end-time', dest = 'e',
                      default = utcmsec, type = int,
                      help =\
                          'the report end time (seconds since the epoch, UTC)')
    parser.add_option('-s', '--time-span', dest = 's',
                      default = 24, type = int,
                      help = 'the time interval spanned (hours)')    
    (opts, args) = parser.parse_args()
    spannedms = int(opts.s*3600000)
    reportGenerator = pReportGenerator(opts.e - spannedms, opts.e,\
                                           opts.c, opts.o)
    reportGenerator.writeReport()
    reportGenerator.compile()

