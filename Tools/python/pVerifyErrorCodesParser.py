
import os
import sys
import time

sys.path.append('/afs/slac.stanford.edu/g/glast/ground/releases/volume13/L1Proc/2.6/dataMonitoring/Common/Common-06-09-00/python')

import pSafeLogger
logger = pSafeLogger.getLogger('pVerifyParser')

from pHtmlWriter import pHtmlWriter
from pXmlWriter  import pXmlWriter


MAIN_TEXT =\
"""
The following table contains some explanations about the Verify error
codes.</br>
"""


class pVerifyErrorCodesParser(pHtmlWriter, pXmlWriter):

    def __init__(self, inputFilePath):
        self.InputFilePath = inputFilePath
        self.ErrorDict = {}
        self.extractVersionString()
        self.extraxtErrorDict()
        self.ErrorCodes = self.ErrorDict.keys()
        self.ErrorCodes.sort()

    def extractVersionString(self):
        (folderPath, fileName) = os.path.split(self.InputFilePath)
        cvsFilePath = os.path.join(folderPath, 'CVS', 'Entries')
        cvsFileContent = file(cvsFilePath).readlines()
        for line in cvsFileContent:
           if fileName in line:
               (version, date) = line.split('/')[2:4]
               self.VersionString = '%s version %s (committed on %s)' %\
                               (fileName, version, date)
               return

    def extraxtErrorDict(self):
        for line in file(self.InputFilePath).readlines():
            try:
                (pattern, content) = line.split('=')
                if pattern.strip() == 'errorName':
                    (errorCode, explanation) = content.split(';')
                    errorCode = errorCode.strip().replace('"', '')
                    explanation = explanation.strip().replace('//', '')
                    explanation = explanation.strip()
                    explanation = explanation.strip("['")
                    explanation = explanation.strip("]'")
                    self.ErrorDict[errorCode] = explanation
            except:
                pass
    
    def writeHtmlTable(self, outputFilePath):
        self.openPage(outputFilePath, 'Verify error codes')
        self.addParagraph(MAIN_TEXT)
        self.addParagraph('Table generated by %s on %s from %s.' %\
                          ('pVerifyErrorCodesParser', time.asctime(),
                           self.VersionString))
        self.openTable(['Error code', 'Description'])
        for errorCode in self.ErrorCodes:
            explanation = self.ErrorDict[errorCode]
            self.writeTableLine([errorCode, explanation])              
        self.closePage()

    def writeXmlAlarmFile(self, outputFilePath):
        pXmlWriter.openFile(self, outputFilePath)
        pXmlWriter.writeComment(self, 'File generated from %s.' %\
                                self.VersionString)
        self.newline()
        pXmlWriter.openTag(self, 'alarms')
        self.newline()
        self.indent()
        pXmlWriter.openTag(self, 'alarmList',
                           {'group':'Main', 'name':'Main', 'enabled':'True'})
        self.newline()
        for errorCode in self.ErrorCodes:
            self.indent()
            pXmlWriter.openTag(self, 'alarmSet',
                               {'name': errorCode, 'enabled': 'True'})
            self.indent()
            pXmlWriter.openTag(self, 'alarm',
                               {'function': 'number', 'enabled': 'True'})
            self.indent()
            pXmlWriter.openTag(self, 'warning_limits',
                               {'min': '0.0', 'max': '0.0'}, True)
            pXmlWriter.openTag(self, 'error_limits',
                               {'min': '0.0', 'max': '0.0'}, True)
            self.backup()
            pXmlWriter.closeTag(self, 'alarm')
            self.backup()
            pXmlWriter.closeTag(self, 'alarmSet')
            self.backup()
            self.newline()
        pXmlWriter.closeTag(self, 'alarmList')
        self.backup()
        pXmlWriter.closeTag(self, 'alarms')
        pXmlWriter.closeFile(self) 


if __name__ == '__main__':
    runVerifyFilePath = '/afs/slac/g/glast/users/monzani/L1Pipeline/TestReport/src/RunVerify.cxx'
    runParser = pVerifyErrorCodesParser(runVerifyFilePath)
    runParser.writeXmlAlarmFile('verify_errors_alarms.xml')
    runParser.writeHtmlTable('verifylog_error_codes.html')
    ft1VerifyFilePath = '/afs/slac/g/glast/users/monzani/L1Pipeline/TestReport/src/ft1Verify.cxx'
    ft1Parser = pVerifyErrorCodesParser(ft1VerifyFilePath)
    ft1Parser.writeXmlAlarmFile('verify_ft1_errors_alarms.xml')
    ft1Parser.writeHtmlTable('verify_ft1_error_codes.html')
    ft2VerifyFilePath = '/afs/slac/g/glast/users/monzani/L1Pipeline/TestReport/src/ft2Verify.cxx'
    ft2Parser = pVerifyErrorCodesParser(ft2VerifyFilePath)
    ft2Parser.writeXmlAlarmFile('verify_ft2_errors_alarms.xml')
    ft2Parser.writeHtmlTable('verify_ft2_error_codes.html')
    meritVerifyFilePath = '/afs/slac/g/glast/users/monzani/L1Pipeline/TestReport/src/meritVerify.cxx'
    MeritParser = pVerifyErrorCodesParser(meritVerifyFilePath)
    MeritParser.writeXmlAlarmFile('verify_merit_errors_alarms.xml')
    MeritParser.writeHtmlTable('verify_merit_error_codes.html')




