#!/bin/env python

import os
import logging
import re
import sys
import time

logging.basicConfig(level = logging.DEBUG)

from pLaTeXWriter     import pLaTeXWriter
from pReportPanel     import pReportPanel
from pReportPage      import pReportPage
from pDownloadManager import pDownloadManager
from pXmlElement      import pXmlElement
from xml.dom          import minidom
from pTimeConverter   import *

# TBD. Use environmental variables here!
BASE_DIR_PATH = os.path.dirname(os.path.abspath(__file__))

PREAMBLE_PATH = os.path.join(BASE_DIR_PATH, 'preamble.tex')
LOGO_IMAGE_PATH = os.path.join(BASE_DIR_PATH, 'glastLogo.png')
DEFAULT_CFG_FILE_PATH = os.path.join(BASE_DIR_PATH, '../xml/summaryReport.xml')
LATEX_TMP_DIR_NAME = 'report_latex_temp_%s' %\
    sec2string(time.time(), FORMAT_STRINGS_DICT['Luca Baldini'])
DOWNLOAD_TMP_DIR_NAME = 'report_download_temp_%s' %\
    sec2string(time.time(), FORMAT_STRINGS_DICT['Luca Baldini'])
COOKIE_TMP_DIR_NAME = 'report_cookie_temp_%s' %\
    sec2string(time.time(), FORMAT_STRINGS_DICT['Luca Baldini'])


class pReportGenerator(pLaTeXWriter, pDownloadManager):
    
    def __init__(self, endTime, spannedTime, pdfFolderPath, cfgFilePath):
        self.TimeStatList = []
        startTime = time.time()
        self.ProcessingStartTime = startTime
        self.DownloadFolderPath =\
            os.path.join(pdfFolderPath, DOWNLOAD_TMP_DIR_NAME)
        self.CookieFolderPath = os.path.join(pdfFolderPath, COOKIE_TMP_DIR_NAME)
        pDownloadManager.__init__(self, self.DownloadFolderPath,\
                                      self.CookieFolderPath)
        self.EndTime = endTime
        self.StartTime = endTime - int(spannedTime*3600000)
        self.TimeSpan = '%s -- %s' %\
            (msec2string(self.StartTime), msec2string(self.EndTime))
        pdfFileName = '%s' % os.path.basename(cfgFilePath).replace('.xml', '')
        pdfFileName += '_%s' % msec2string(self.EndTime, '%Y-%j-%Hh%Mm%Ss')
        pdfFileName += ('_%.2f' % spannedTime).replace('.', 'h')
        #pdfFileName += '_%s' % sec2string(time.time(), '%y%j%H%M%S')
        pdfFileName += '.pdf'
        latexFilePath = os.path.join(pdfFolderPath, LATEX_TMP_DIR_NAME,\
                                         pdfFileName.replace('.pdf','.tex'))
        self.PdfFilePath = os.path.join(pdfFolderPath, pdfFileName)
        logging.info('Output folder  : %s' % os.path.abspath(pdfFolderPath))
        logging.info('pdf file name  : %s' % pdfFileName)
        logging.info('Download folder: %s' %\
                         os.path.abspath(self.DownloadFolderPath))
        logging.info('LaTeX file path: %s' % os.path.abspath(latexFilePath))
        pLaTeXWriter.__init__(self, latexFilePath)
        self.fillTimeStat('Inizialitation', time.time() - startTime)
        logging.info('Parsing xml configuration file %s...' %\
                         os.path.abspath(cfgFilePath))
        try:
            self.XmlBaseElement = pXmlElement(minidom.parse(file(cfgFilePath)))
        except:
            sys.exit('Could not parse xml configuration file. Abort.')
        logging.info('Done.')
        self.PagesList = []
        self.PanelsDict = {}
        self.parseConfiguration()
        self.invalidateSession()

    def fillTimeStat(self, operation, elapsedTime):
        self.TimeStatList.append('%40s: %.2f s' % (operation, elapsedTime))

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
                            startTime = time.time()
                            panel = pReportPanel(panelName, self.StartTime,\
                                                     self.EndTime,\
                                                     self.LaTeXFolderPath,\
                                                     self.DownloadFolderPath,\
                                                     self.CookieFolderPath)
                            self.PanelsDict[panelName] = panel
                            self.fillTimeStat(('Download panel "%s"' %\
                                                   panelName),\
                                                  time.time() - startTime)
                        else:
                            logging.info('Panel %s already downloaded.' %\
                                         panelName)
                            panel = self.PanelsDict[panelName]
                        page.addPanel(panel)
                self.PagesList.append(page)

    def writeReport(self):
        startTime = time.time()
        self.writeHeader()
        logging.info('Copying the GLAST logo into the report folder...')
        os.system('cp %s %s' % (LOGO_IMAGE_PATH, self.LaTeXFolderPath))
        logging.info('Copying the TeX preamble into the report folder...')
        os.system('cp %s %s' % (PREAMBLE_PATH, self.LaTeXFolderPath))
        for page in self.PagesList:
            self.addPage(page, self.Title, self.TimeSpan)
        self.writeTrailer()
        self.fillTimeStat('Write LaTeX report', time.time() - startTime)
        startTime = time.time()
        self.compile()
        self.fillTimeStat('Compile LaTeX report', time.time() - startTime)

    def copyPdfAndCleanUp(self, cleanupLaTeX):
        startTime = time.time()
        os.system('cd %s; cp *.pdf ..' % self.LaTeXFolderPath)
        if cleanupLaTeX:
            os.system('rm -rf %s' % self.LaTeXFolderPath)
        self.fillTimeStat('Cleanup', time.time() - startTime)
        self.ProcessingStopTime = time.time()
        print '\n**************** Statistiscs ********************'
        for label in self.TimeStatList:
            print label 
        print
        print '%40s: %.2f s' % ('Total elapsed time',
                                self.ProcessingStopTime -\
                                    self.ProcessingStartTime)
        print '***************************************************\n'
 

if __name__ == '__main__':
    import time
    utcmsec = time.time()
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options]')
    parser.add_option('-c', '--config-file', dest = 'c',
                      default = DEFAULT_CFG_FILE_PATH, type = str,
                      help = 'path to the input xml config file')
    parser.add_option('-d', '--dir-path', dest = 'd',
                      default = './report', type = str,
                      help = 'path to the folder for the output pdf file')
    parser.add_option('-e', '--end-time', dest = 'e',
                      default = utcmsec,
                      help = 'the report UTC end time (in s or as a string)')
    parser.add_option('-s', '--time-span', dest = 's',
                      default = 24, type = int,
                      help = 'the time interval spanned (in hours)')
    parser.add_option('-t', '--time-formats',
                      action='store_true', dest='t', default=False,
                      help='print the list of avilable time formats and exit')
    parser.add_option('-l', '--do-not-cleanup-LaTeX',
                      action='store_false', dest='l', default=True,
                      help='do not clean up the temporary LaTeX folde')
    (opts, args) = parser.parse_args()
    if opts.t:
        print 'Available format strings for specifying end time:\n%s' %\
            availableTimeFormats()
        sys.exit()
    endms = convert2msec(opts.e)
    reportGenerator = pReportGenerator(endms, opts.s, opts.d, opts.c)
    reportGenerator.writeReport()
    reportGenerator.copyPdfAndCleanUp(opts.l)
