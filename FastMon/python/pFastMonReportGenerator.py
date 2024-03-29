#! /bin/env python

## @package pTestReportGenerator
## @brief Package for generating test reports.

import pSafeLogger
logger = pSafeLogger.getLogger('pFastMonReportGenerator')

import os
import sys
import commands
import time

from pXmlParser           import pXmlParser
from pBaseReportGenerator import pBaseReportGenerator
from pSafeROOT            import ROOT
from pRootFileManager     import pRootFileManager


class pFastMonBaseReportGenerator(pBaseReportGenerator):

    def __init__(self, reportDirPath = None):
        pBaseReportGenerator.__init__(self, reportDirPath)

    def run(self, verbose = False):
        logger.info('Writing doxygen report files...')
        startTime = time.time()
        self.RootFileManager.openFile(self.RootFilePath)
        self.openReport()
        self.fillMainPage()
        self.addErrors()
        self.createAuxRootCanvas(True, verbose)
        self.addPlots()
        self.deleteAuxRootCanvas()
        self.closeReport()
        self.RootFileManager.closeFile()
        logger.info('Done in %.2f s.\n' % (time.time() - startTime))
        self.compileReport(verbose)

    def addPlots(self):
        for list in self.XmlParser.OutputListsDict.values():
            if list.Enabled:
                self.addPlotsList(list)

    def addErrors(self):
        if self.ErrorHandler is not None:
            self.addErrorSummary()
            self.addErrorDetails()

    def addErrorSummary(self):
        pageLabel = 'error_summary'
        pageTitle = 'Error handler summary'
        self.addPage(pageLabel, pageTitle)
        self.newline(pageLabel)
        self.write('Here is the number of errors found in the run ' +\
                   '(indexed by error code)', pageLabel)
        self.newline(pageLabel)
        dictionary = self.ErrorHandler.ErrorCountsDict
        if len(dictionary):
            self.addDictionary('Summary by error code', dictionary, pageLabel)
        else:
            self.write('No error(s) found in this run.', pageLabel)

    def addErrorDetails(self):
        pageLabel = 'error_details'
        pageTitle = 'Error handler details'
        self.addPage(pageLabel, pageTitle)
        self.newline(pageLabel)
        self.write('Here is the detailed list of events with error(s)',\
                   pageLabel)
        self.newline(pageLabel)
        if self.ErrorHandler.getNumErrorEvents() > 0:
            for errorEvent in self.ErrorHandler.ErrorEventsList:
                self.addDictionary('Event %d' %\
                                       errorEvent.EventNumber,\
                                       errorEvent.getErrorsDict(),\
                                       'error_details')
        else:
            self.write('No error(s) found in this run.', pageLabel)



class pStandaloneFastMonReportGenerator(pFastMonBaseReportGenerator):

    MAIN_PAGE_TITLE = 'Report Generator'
    REPORT_AUTHOR   = 'Automatically generated by ' +\
                      'pStandaloneFastMonReportGenerator'
    
    def __init__(self, errorFilePath, xmlConfigFilePath,\
                 rootProcessedFilePath, reportDirPath = None):
        from pErrorHandler import pErrorHandler
        from pXmlParser    import pXmlParser
        self.ErrorHandler = pErrorHandler()
        pickleErrorFilePath = errorFilePath
        try:
            pickleErrorFilePath = errorFilePath.replace('.xml', '.pickle')
            self.ErrorHandler.load(pickleErrorFilePath)
        except:
            logger.error('Could not unpickle %s.'% pickleErrorFilePath)
            logger.warn('The report will not contain errors (if any).')
            self.ErrorHandler = None
        self.XmlParser = pXmlParser(xmlConfigFilePath)
        self.RootFilePath  = rootProcessedFilePath
        if reportDirPath is None:
            reportDirPath = self.RootFilePath.replace('.root', '_report')
        pFastMonBaseReportGenerator.__init__(self, reportDirPath)
        self.RootFileManager = pRootFileManager()
        
    def fillMainPage(self):
        self.addSection('main_summary', 'Summary')
        if self.ErrorHandler is not None:
            self.write('There are %d error(s) in %d error event(s).' %\
                           (self.ErrorHandler.getNumErrors(),
                            self.ErrorHandler.getNumErrorEvents()))
        self.newline()
        self.write('@n Look at the related pages for details.')



class pFastMonReportGenerator(pFastMonBaseReportGenerator):

    MAIN_PAGE_TITLE = 'Fast monitor report'
    REPORT_AUTHOR   = 'Automatically generated by pDataProcessor.py'

    def __init__(self, dataProcessor, reportDirPath = None):
        self.DataProcessor = dataProcessor
        self.ErrorHandler = self.DataProcessor.ErrorHandler
        self.XmlParser = self.DataProcessor.XmlParser
        self.RootFilePath = self.DataProcessor.TreeProcessor.OutputFilePath
        if reportDirPath is None:
            reportDirPath = self.RootFilePath.replace('.root', '_report')
        pBaseReportGenerator.__init__(self, reportDirPath)
        self.RootFileManager = pRootFileManager()

    def fillMainPage(self):
        self.addSection('main_summary', 'Summary')
        self.write('%d event(s) processed in %.2f seconds.' %\
                   (self.DataProcessor.NumEvents,\
                    self.DataProcessor.StopTime -\
                    self.DataProcessor.StartTime))
        self.newline()
        if self.ErrorHandler is not None:
            self.write('There are %d error(s) in %d error event(s).' %\
                           (self.ErrorHandler.getNumErrors(),
                            self.ErrorHandler.getNumErrorEvents()))
        self.newline()
        self.write('@n Look at the related pages for details.')


if __name__ == '__main__':
    from pOptionParser import pOptionParser
    optparser = pOptionParser('cvVe',1,1,False)
    reportGenerator = pStandaloneFastMonReportGenerator(optparser.Options.e,\
                                                        optparser.Options.c,\
                                                        optparser.Argument)
    reportGenerator.run(optparser.Options.v)
    if optparser.Options.V:
        reportGenerator.viewReport()
