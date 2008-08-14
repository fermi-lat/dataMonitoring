from pHtmlWriter import *

MAIN_TEXT =\
"""
The following table contains the correspondence between </br>
TileId</br>
CableA	FREENAMEA	ChannelA </br>
CableB	FREENAMEB	ChannelB </br>
Tile/ribbon number	Type	Active area (cm^2))</br>
"""

class pACDMapParser(pHtmlWriter):
    
    def writeTable(self, outputFilePath):
        self.openPage(outputFilePath, 'ACD Mapping')
        self.addParagraph(MAIN_TEXT)
        self.writeTableFromFile('acd_map.txt')
        self.closePage()



if __name__ == '__main__':
    parser = pACDMapParser()
    parser.writeTable('acd_map.html')
