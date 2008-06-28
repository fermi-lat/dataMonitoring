
import logging
logging.basicConfig(level = logging.DEBUG)

import os
import sys
import time
import lrsUtils

from lrsTreeWriter import lrsTreeWriter


class lrsConverter(lrsTreeWriter):

    TREE_NAME     = 'LrsTree'

    def __init__(self, inputCsvFilePath):
        if not os.path.exists(inputCsvFilePath):
            sys.exit('Could not find %s. Abort.' % inputCsvFilePath)
        outputRootFilePath = inputCsvFilePath.replace('.csv', '.root')
        lrsTreeWriter.__init__(self, outputRootFilePath, self.TREE_NAME,\
                                   self.BRANCHES_LIST)
        self.InputCsvFile = file(inputCsvFilePath)
        self.LineNumber = 0
        self.FirstTimestamp = lrsUtils.getFirstTimestamp(inputCsvFilePath)
        self.LastTimestamp = lrsUtils.getLastTimestamp(inputCsvFilePath,\
                                                           self.DATA_BLOCK_SIZE)
        self.BeginDate = lrsUtils.utc2string(self.FirstTimestamp)
        self.EndDate = lrsUtils.utc2string(self.LastTimestamp)
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
        return lrsUtils.met2utc(timestamp)
