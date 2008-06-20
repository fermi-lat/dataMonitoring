
import sys
sys.path.append('../../Common/python')

from pAlarmUtils import *
from pHtmlWriter import *


MAIN_TEXT =\
"""
The following table maps the tile/ribbon numbers (0--127, as encoded in all the
data monitoring application plots) to the actual type and active area.</br>

The numbers 89--95, 104--127, though appearing in the data monitoring plots,
are not mapped to any actual tile or ribbon and are there essentially for
convenience and/or historical reasons.</br>

Disclaimer: the numbers are indicative and come with absolutely no warranty.
We do not assume any responsibility if they screw up your analisys. 
"""

class pAcdTileMapper(pHtmlWriter):

    def writeTable(self, outputFilePath):
        self.openPage(outputFilePath, 'ACD tile mapping and active area')
        self.addParagraph(MAIN_TEXT)
        self.openTable(['Tile/ribbon number', 'Type', 'Active area (cm^2)'])
        for i in range(128):
            self.writeTableLine([i, getAcdTileType(i), getAcdTileArea(i)])
        self.closePage()


if __name__ == '__main__':
    mapper = pAcdTileMapper()
    mapper.writeTable('acd_tile_area.html')
