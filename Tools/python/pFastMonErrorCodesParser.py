

from pHtmlWriter import *

import sys
sys.path.append('../../FastMon/python')

from pError      import *
from pErrorEvent import *


MAIN_TEXT =\
"""
The following table contains some explanations about the FastMon error
codes.</br>

The FastMon tuple contains an unsigned int (32 bits) variable called
error_summary encoding all the errors (if any) in the event. The correspondence
between the error codes and the relative summary bits is contained
in the table as well.
"""

class pFastMonErrorCodesParser(pHtmlWriter):
    
    def writeTable(self, outputFilePath):
        self.openPage(outputFilePath, 'FastMon error codes')
        self.addParagraph(MAIN_TEXT)
        self.openTable(['Error code', 'Description', 'Summary bit',\
                            'Summary value'])
        errorCodes = ERROR_DETAIL_LABELS_DICT.keys()
        errorCodes.sort()
        for errorCode in errorCodes:
            summaryBit = ERROR_BITS_DICT[errorCode]
            summaryValue = 2**summaryBit
            summaryLabel = '0x%x (decimal %d)' % (summaryValue, summaryValue)
            explanation = getExplanation(errorCode)
            self.writeTableLine([errorCode, explanation, summaryBit,\
                                     summaryLabel])
        self.closePage()


if __name__ == '__main__':
    parser = pFastMonErrorCodesParser()
    parser.writeTable('fastmonerror_error_codes.html')
