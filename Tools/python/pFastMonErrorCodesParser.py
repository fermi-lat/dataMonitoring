

from pHtmlWriter import *

import sys
sys.path.append('../../FastMon/python')

from pError import *


MAIN_TEXT =\
"""
The following table contains some explanations about the FastMon error
codes.</br>
"""

class pFastMonErrorCodesParser(pHtmlWriter):
    
    def writeTable(self, outputFilePath):
        self.openPage(outputFilePath, 'FastMon error codes')
        self.addParagraph(MAIN_TEXT)
        self.openTable(['Error code', 'Description'])
        errorCodes = ERROR_DETAIL_LABELS_DICT.keys()
        errorCodes.sort()
        for errorCode in errorCodes:
            explanation = getExplanation(errorCode)
            self.writeTableLine([errorCode, explanation])
        self.closePage()


if __name__ == '__main__':
    parser = pFastMonErrorCodesParser()
    parser.writeTable('fastmonerror_error_codes.html')
