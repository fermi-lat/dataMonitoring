

from pHtmlWriter import *

ERROR_CODE_FILE_PATH = '../../FastMon/doc/ErrorCodes.txt'


MAIN_TEXT =\
"""
The following table contains some explanations about the FastMon error
codes.</br>
"""

class pFastMonErrorCodeParser(pHtmlWriter):
    
    def writeTable(self, outputFilePath):
        self.openPage(outputFilePath, 'FastMon error codes')
        self.addParagraph(MAIN_TEXT)
        self.writeTableFromFile(ERROR_CODE_FILE_PATH)
        self.closePage()


if __name__ == '__main__':
    parser = pFastMonErrorCodeParser()
    parser.writeTable('fast_mon_error_codes.html')
