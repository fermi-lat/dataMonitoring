#!/bin/env python

import pSafeLogger
logger = pSafeLogger.getLogger('pTreeProcessor')

import sys
import os
import time

from pXmlBaseParser       import pXmlBaseParser
from pBaseTreeProcessor   import pBaseTreeProcessor
from pBaseReportGenerator import pBaseReportGenerator
from pRootFileManager     import pRootFileManager


class pTreeProcessorXmlParser(pXmlBaseParser):

    def __init__(self, configFilePath = None):
        pXmlBaseParser.__init__(self, configFilePath)
        logger.info('Reading the output lists...')
        self.InputRootTreeName   = self.getInputRootTreeName()
        self.EnabledPlotLists    = self.getEnabledPlotLists()
        self.EnabledPlotRepsDict = {}
        for list in self.EnabledPlotLists:
            for (key, value) in list.EnabledPlotRepsDict.items():
                self.EnabledPlotRepsDict[key] = value
        logger.info('%d enabled plots found in the output lists.' %\
                    len(self.EnabledPlotRepsDict))


class pTreeProcessorReportGenerator(pBaseReportGenerator):

    MAIN_PAGE_TITLE = 'Tree processor monitor report'
    REPORT_AUTHOR   = 'Automatically generated by pTreeProcessor.py'

    def __init__(self, treeProcessor):
        self.TreeProcessor = treeProcessor
        self.RootFilePath  = self.TreeProcessor.OutputFilePath
        reportDirPath = self.RootFilePath.replace('.root', '.report')
        pBaseReportGenerator.__init__(self, reportDirPath)
        self.RootFileManager = pRootFileManager()

    def run(self, verbose = False, compileLaTeX = True):
        logger.info('Writing doxygen report files...')
        startTime = time.time()
        self.RootFileManager.openFile(self.RootFilePath)
        self.openReport()
        self.fillMainPage()
        self.addPlots()
        self.closeReport()
        self.RootFileManager.closeFile()
        logger.info('Done in %.2f s.\n' % (time.time() - startTime))
        self.compileReport(verbose, compileLaTeX)
        
    def fillMainPage(self):
        self.addSection('main_summary', 'Summary')
        self.write('@n Look at the related pages for details.')

    def addPlots(self):
        for list in self.TreeProcessor.XmlParser.EnabledPlotLists:
            self.addPlotList(list)

    ## There's a clear conflict with the FastMon stuff, here.
    ## To be fixed.

    def addPlotList(self, list):
        pageLabel = 'list_%s' % list.Name.replace(' ', '_')
        pageTitle = '%s plots list' % list.Name
        self.addPage(pageLabel, pageTitle)
        for plotRep in list.EnabledPlotRepsDict.values():
            self.addPlot(plotRep, plotRep.Name, pageLabel)


class pTreeProcessor(pBaseTreeProcessor):

    def __init__(self, xmlParser, inputFilePath, outputFilePath = None):
        rootTreeName = xmlParser.InputRootTreeName
        pBaseTreeProcessor.__init__(self, xmlParser, inputFilePath,\
                                    rootTreeName, outputFilePath)


if __name__ == '__main__':
    from pOptionParser import pOptionParser
    optparser = pOptionParser('corvLVn')
    parser    = pTreeProcessorXmlParser(optparser.Options.c)
    processor = pTreeProcessor(parser, optparser.Argument)
    processor.run(optparser.Options.n)
    if optparser.Options.r:
        reportGenerator = pTreeProcessorReportGenerator(processor)
        reportGenerator.run(optparser.Options.v, not optparser.Options.L)
        if optparser.Options.V:
            reportGenerator.viewReport()
