
import logging
logging.basicConfig(level = logging.DEBUG)

import sys
import os


class pAsciiWriter:
    
    NUM_INDENT_SPACES = 2

    def __init__(self, filePath = None):        
        self.OutputFile  = None
        self.IndentLevel = None
        if filePath is not None:
            self.openFile(filePath)

    def openFile(self, filePath):
        logging.debug('Opening file %s...' % filePath)
        self.OutputFile = file(filePath, 'w')
        self.setIndentLevel(0)

    def closeFile(self):
        logging.debug('Closing file...')
        if self.OutputFile is not None:
            self.OutputFile.close()
            self.OutputFile  = None
            self.IndentLevel = None
    
    def setIndentLevel(self, level):
        if level >= 0:
            self.IndentLevel = level
        else:
            logging.warning('Negative indent level requested, set to 0.')
            self.IndentLevel = 0
    
    def indent(self, numLevels = 1):
        self.setIndentLevel(self.IndentLevel + numLevels)

    def backup(self, numLevels = 1):
        self.setIndentLevel(self.IndentLevel - numLevels)

    def write(self, text):
        if self.OutputFile is not None:
            self.OutputFile.writelines(text)
        else:
            logging.error('Output file not existing.')
            sys.exit('Abort.')

    def newline(self):
        self.write('\n')

    def writeIndented(self, text):
        spaces = self.IndentLevel*self.NUM_INDENT_SPACES*' '
        self.write('%s%s' % (spaces, text))


if __name__ == '__main__':
    writer = pAsciiWriter('ascii_test.txt')

