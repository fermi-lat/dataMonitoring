
from pHtmlWriter import *


MAIN_TEXT =\
"""
The following table contains some explanations about the Verify error
codes.</br>
"""


class pVerifyErrorCodesParser(pHtmlWriter):
    
    def writeTable(self, inputFilePath, outputFilePath):
        self.openPage(outputFilePath, 'Verify error codes')
        self.addParagraph(MAIN_TEXT)
        self.openTable(['Error code', 'Description'])
        for line in file(inputFilePath).readlines():
            try:
                (pattern, content) = line.split('=')
                if pattern.strip() == 'errorName':
                    (errorCode, explanation) = content.split(';')
                    errorCode = errorCode.strip().replace('"', '')
                    explanation = explanation.strip().replace('//', '')
                    self.writeTableLine([errorCode, explanation])
            except:
                pass
        self.closePage()


if __name__ == '__main__':
    inputFilePath = '/data/work/isoc/svac/TestReport/src/RunVerify.cxx'
    parser = pVerifyErrorCodesParser()
    parser.writeTable(inputFilePath, 'run_verify_error_codes.html')
