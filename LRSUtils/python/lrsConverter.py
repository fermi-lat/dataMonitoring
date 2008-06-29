
import logging
logging.basicConfig(level = logging.DEBUG)

import os
import sys
import time
import ROOT
from lrsUtils import *

from lrsTreeWriter import lrsTreeWriter


class lrsConverter(lrsTreeWriter):

    TREE_NAME     = 'LrsTree'
    MNEMONICS_LIST = ['LSPECIDECZ',
                      'LSPECIRAZ',
                      'LSPGALDECZ',
                      'LSPGALRAZ',
                      'LSPGEOALT',
                      'LSPGEOLAT',
                      'LSPGEOLON',
                      'LSPMAGLAT',
                      'LSPMAGLON',
                      'LSPMAGRAD',
                      'LSPMCILWAINB',
                      'LSPMCILWAINL',
                      'LSPORBRAD',
                      'LSPPCUTOFF',
                      'LSPROCKANGLE',
                      'LSPSUNANGLE',
                      'SACFLAGLATINSAA'
                      ]

    def __init__(self, inputCsvFilePath):
        if not os.path.exists(inputCsvFilePath):
            sys.exit('Could not find %s. Abort.' % inputCsvFilePath)
        outputRootFilePath = inputCsvFilePath.replace('.csv', '.root')
        for mnemonic in self.MNEMONICS_LIST:
            self.BRANCHES_LIST.append('%s:d:(1)' % mnemonic)
        lrsTreeWriter.__init__(self, outputRootFilePath, self.TREE_NAME,\
                                   self.BRANCHES_LIST)
        self.InputCvsFilePath = inputCsvFilePath
        self.InputCsvFile = file(inputCsvFilePath)
        self.LineNumber = 0
        self.FirstTimestamp = getFirstTimestamp(inputCsvFilePath)
        self.LastTimestamp = getLastTimestamp(inputCsvFilePath,\
                                                           self.DATA_BLOCK_SIZE)
        self.BeginDate = utc2string(self.FirstTimestamp)
        self.EndDate = utc2string(self.LastTimestamp)
        logging.info('Data found between %s and %s.' %\
                         (self.BeginDate, self.EndDate))
        self.retrieveNavigationInformation()
        self.retrieveSAAInformation()

    def retrieveNavigationInformation(self):
        navFilePath = self.InputCvsFilePath.replace('.csv', '_nav.txt')
        if not os.path.exists(navFilePath):
            sys.exit('Could not find %s. Abort.' % navFilePath)
        self.NavigationGraphList = []
        self.NavigationMnemonicsDict = {}
        navigationFile = file(navFilePath)
        for i in range(2):
            navigationFile.readline()
        self.NavigationMnemonics =\
            navigationFile.readline().strip('\n').split(',')[2:]
        for (i, label) in enumerate(self.NavigationMnemonics):
            graph = ROOT.TGraph()
            graph.SetNameTitle(label, label)
            self.NavigationGraphList.append(graph)
            self.NavigationMnemonicsDict[label] = i
        for (lineNumber, line) in enumerate(navigationFile.readlines()):
            data = line.strip('\n').split(',')
            time = string2utc(data[0], NAVIGATION_TIME_FORMAT)
            data[1:] = [float(x) for x in data[1:]]
            for i in range(len(self.NavigationMnemonics)):
                self.NavigationGraphList[i].SetPoint(lineNumber,\
                                                         time, data[i + 2])

    def getNavigationData(self, timestamp, mnemonic):
        i = self.NavigationMnemonicsDict[mnemonic]
        return self.NavigationGraphList[i].Eval(timestamp)

    def retrieveSAAInformation(self):
        saaFilePath = self.InputCvsFilePath.replace('.csv', '_saa.txt')
        if not os.path.exists(saaFilePath):
            sys.exit('Could not find %s. Abort.' % saaFilePath)
        self.SAAGraph = ROOT.TGraph()
        self.SAAGraph.SetNameTitle('SACFLAGLATINSAA', 'SACFLAGLATINSAA')
        saaFile = file(saaFilePath)
        saaFile.readline()
        for (lineNumber, line) in enumerate(saaFile.readlines()):
            data = line.strip('\n').split(',')
            data[1:] = [float(x) for x in data[1:]]
            self.SAAGraph.SetPoint(lineNumber, data[1], data[2])
        sys.exit()

    def getSAAFlag(self, timestamp):
        return self.SAAGraph.Eval(timestamp)

    def drawNavigationGraphs(self):
        for (i, label) in enumerate(self.NavigationMnemonics):
            self.NavigationGraphList[i].Draw('ALP')
            ROOT.gPad.Update()
            raw_input()
            
    def drawSAAGraph(self):
        self.SAAGraph.Draw('ALP')
        ROOT.gPad.Update()
        raw_input()

    def fillTelemetryInformation(self, timestamp):
        for mnemonic in self.NavigationMnemonics:
            self.getArray(mnemonic)[0] =\
                self.getNavigationData(timestamp, mnemonic)
        self.getArray('SACFLAGLATINSAA')[0] = self.getSAAFlag(timestamp)

    def close(self):
        logging.info('Closing files...')
        self.closeTree()
        self.InputCsvFile.close()

    def line(self):
        self.LineNumber += 1
        if self.LineNumber%100000 == 0:
            logging.debug('%d lines read.' % self.LineNumber)
        return self.InputCsvFile.readline()
    
    def exit(self, message = None):
        if message is not None:
            logging.error(message)
        sys.exit('Problems reading file at line %d. Abort.' % self.LineNumber)

    def timestamp(self):
        timestamp = self.line()
        if timestamp == '':
            return None
        timestamp = float(timestamp)
        return met2utc(timestamp)
