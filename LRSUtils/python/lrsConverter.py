
import logging
logging.basicConfig(level = logging.DEBUG)

import os
import sys
import time

from lrsTreeWriter import lrsTreeWriter


MET_OFFSET = 978307200
DEFAULT_TIME_FORMAT = '%d-%b-%Y %H:%M:%S'
BRYSON_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'

class lrsConverter(lrsTreeWriter):

    TREE_NAME     = 'LrsTree'

    def __init__(self, inputCsvFilePath):
        if not os.path.exists(inputCsvFilePath):
            sys.exit('Could not find %s. Abort.' % inputCsvFilePath)
        outputRootFilePath = inputCsvFilePath.replace('.csv', '.root')
        lrsTreeWriter.__init__(self, outputRootFilePath, self.TREE_NAME,\
                                   self.BRANCHES_LIST)
        self.InputCvsFilePath = inputCsvFilePath
        self.InputCsvFile = file(self.InputCvsFilePath)
        self.LineNumber = 0
        self.FirstTimestamp = self.getFirstTimestamp()
        self.LastTimestamp = self.getLastTimestamp()
        self.BeginDate = self.utc2string(self.FirstTimestamp)
        self.EndDate = self.utc2string(self.LastTimestamp)
        logging.info('Data found between %s and %s.' %\
                         (self.BeginDate, self.EndDate))

    def getNavigationInformation(self):
        navFilePath = self.InputCvsFilePat.replace('.cvs', '_nav.txt')
        command = 'source /u/gl/glastops/flightops.csh;'
        command += 'DiagRet.py --nav -b "%s" -e "%s" >> %s' %\
            (self.BeginDate, self.EndDate, navFilePath)
        logging.info('About to execute command "%s".' % command)

    def getSAAInformation(self):
        saaFilePath = self.InputCvsFilePat.replace('.cvs', '_saa.txt')
        command = 'source /u/gl/glastops/flightops.csh;'
        command += 'MnemRet.py --csv %s -b -b "%s" -e "%s" SACFLAGLATINSAA'%\
            (saaFilePath, self.BeginDate, self.EndDate)
        logging.info('About to execute command "%s".' % command)

    def close(self):
        logging.info('Closing files...')
        self.closeTree()
        self.InputCsvFile.close()

    def met2utc(self, met):
        return met + MET_OFFSET

    def utc2string(self, utc, stringFormat = BRYSON_TIME_FORMAT):
        return time.strftime(stringFormat, time.gmtime(utc))

    def getFirstTimestamp(self):
        timestamp = self.timestamp()
        self.InputCsvFile.seek(0)
        return timestamp

    def getLastTimestamp(self):
        fileSize = os.stat(self.InputCvsFilePath)[6]
        numLinesFound = 0
        filePosition = fileSize
        while numLinesFound <= self.DATA_BLOCK_SIZE:
            self.InputCsvFile.seek(filePosition)
            item = self.InputCsvFile.read(1)
            if item == '\n':
                numLinesFound += 1
            filePosition -= 1
        timestamp = self.timestamp()
        self.InputCsvFile.seek(0)
        return timestamp

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
        return self.met2utc(timestamp)
