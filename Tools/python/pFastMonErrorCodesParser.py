

from pHtmlWriter import *

ERROR_CODE_FILE_PATH = '../../FastMon/doc/ErrorCodes.txt'


MAIN_TEXT =\
"""
The following table contains some explanations about the FastMon error
codes.</br>
"""

class pFastMonErrorCodesParser(pHtmlWriter):
    
    def writeTable(self, outputFilePath):
        self.openPage(outputFilePath, 'FastMon error codes')
        self.addParagraph(MAIN_TEXT)
        self.writeTableFromFile(ERROR_CODE_FILE_PATH)
        self.closePage()


if __name__ == '__main__':
    parser = pFastMonErrorCodesParser()
    parser.writeTable('fastmonerror_error_codes.html')
