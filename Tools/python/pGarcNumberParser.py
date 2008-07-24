from pHtmlWriter import *

MAIN_TEXT =\
"""
The following table contains the correspondence between the GARC
number and the GARC id.</br>
"""

class pGarcNumberParser(pHtmlWriter):
    
    def writeTable(self, outputFilePath):
        self.openPage(outputFilePath, 'GARC numbers')
        self.addParagraph(MAIN_TEXT)
        self.writeTableFromFile('garc_table.txt')
        self.closePage()



if __name__ == '__main__':
    parser = pGarcNumberParser()
    parser.writeTable('garc_table.html')
