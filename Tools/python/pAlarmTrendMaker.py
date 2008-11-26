#! /bin/env python

import sys

sys.path.append('../../Report/python')
sys.path.append('../../Common/python')

from pSafeROOT import ROOT

import pSafeLogger
logger = pSafeLogger.getLogger('pXmlAlarmTrendMaker')

from pLongTermTrendMaker import *
from pTimeConverter      import *
from pXmlBaseParser      import pXmlBaseParser
from pXmlBaseElement     import pXmlBaseElement

DEFAULT_SITE = '/Data/Flight/Level1/LPA'


class pAlarmTrendMaker(pBaseFileAnalyzer):

    def __init__(self, fileListPath, outputFilePath, group, plotName, algName,
                 minStartTime, maxStartTime = None):
        self.LabelList = [plotName]
        self.QuantityList = [algName]
        pBaseFileAnalyzer.__init__(self, fileListPath, outputFilePath, group,
                                   minStartTime, maxStartTime)

    def run(self):
        for filePath in self.FileList:
            print 'Analyzing %s...' % filePath
            fileName = os.path.basename(filePath)
            self.Arrays['RunId'][0] = int(fileName.split('_')[0].strip('r'))
            print self.getValue(filePath)
            self.OutputTree.Fill()
        self.OutputFile.cd()
        self.OutputTree.Write()
        self.OutputFile.Close()

    def getValue(self, filePath):
        parser = pXmlBaseParser(filePath)
        for plotElement in parser.XmlDoc.getElementsByTagName('plot'):
            plotName = plotElement.getAttribute('name')
            if plotName == self.LabelList[0]:
                plotElement = pXmlBaseElement(plotElement)
                for algElement in plotElement.getElementsByTagName('alarm'):
                    if algElement.getAttribute('function') ==\
                       self.QuantityList[0]:
                        algElement = pXmlBaseElement(alarmElement)
                        outputValue = alarmElement.evalTagValue('output')
                        return outputValue
                        

if __name__ == '__main__':
    MIN_START_TIME = utc2met(convert2sec('Nov/23/2008 00:00:00'))
    MAX_START_TIME = None
    trendMaker = pAlarmTrendMaker('ACDPEDSALARM.txt',
                                  'ACDPEDSALARM.root',
                                  'ACDPEDSALARM',
                                  'AcdPedPedMeanDeviation_PMTA_TH1',
                                  'y_values',
                                  MIN_START_TIME,
                                  MAX_START_TIME)
    trendMaker.run()
