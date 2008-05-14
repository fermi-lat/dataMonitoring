#!/bin/env python

import os
import logging
import re
import sys

logging.basicConfig(level = logging.DEBUG)

from pLaTeXWriter     import pLaTeXWriter
from pReportPanel     import pReportPanel
from pReportPage      import pReportPage
from pDownloadManager import pDownloadManager
from pXmlElement      import pXmlElement
from xml.dom          import minidom


LOGO_IMAGE_NAME = 'glastLogo.png'
PREAMBLE_NAME = 'preamble.tex'
    

class pReportGenerator(pLaTeXWriter, pDownloadManager):
    
    def __init__(self, startTime, endTime, cfgFilePath, outputFilePath):
        pDownloadManager.__init__(self)
        pLaTeXWriter.__init__(self, outputFilePath)
        self.StartTime = startTime
        self.EndTime = endTime
        self.TimeSpan = 'N/A'
        self.XmlBaseElement = pXmlElement(minidom.parse(file(cfgFilePath)))
        self.PagesList = []
        self.PanelsDict = {}
        self.parseConfiguration()

    def parseConfiguration(self):
        reportTag = self.XmlBaseElement.getElementByTagName('report')
        for pageTag in reportTag.getElementsByTagName('page'):
            if pageTag.evalAttribute('enabled'):
                page = pReportPage()
                for panelTag in pageTag.getElementsByTagName('panel'):
                    if panelTag.evalAttribute('enabled'):
                        panelName = panelTag.getAttribute('name')
                        if panelName not in self.PanelsDict.keys():
                            panel = pReportPanel(panelName, self.StartTime,\
                                                 self.EndTime)
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
        self.processIndex()
        for page in self.PagesList:
            self.addPage(page, self.TimeSpan)
        self.processIndex()
        self.writeTrailer()

    def processIndex(self):
        self.downloadBaseReportUrl()
        for line in file('%s/index.html' % self.DownloadFolder).readlines():
            #if 'Panel' in line and 'href' in line:
            #    panelName = re.search('(?<=reportId=).*(?=">)', line).group()
            #    self.PanelsList.append(panelName)
            if 'UTC' in line:
                self.TimeSpan =\
                     line.strip().replace('<b>', '').replace('</b>', '')
        pDownloadManager.cleanup(self)

 

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options]')
    parser.add_option('-c', '--config-file', dest = 'c',
                      default = None, type = str,
                      help = 'path to the input xml config file')
    parser.add_option('-o', '--output-file', dest = 'o',
                      default = './tex/report.tex', type = str,
                      help = 'path to the output TeX file')
    (opts, args) = parser.parse_args()
    if opts.c is None:
        parser.print_help()
        parser.error('Please provide the path to the xml config file.')
    
    startTime = 1208649599000 - 3600*1000*24
    endTime  = 1208649599000
    reportGenerator = pReportGenerator(startTime, endTime, opts.c, opts.o)
    reportGenerator.writeReport()
    reportGenerator.compile()

