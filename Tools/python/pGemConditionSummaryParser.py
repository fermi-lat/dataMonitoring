
from pHtmlWriter import *


BITS_LIST = ['ROI', 'TKR', 'CAL_LO', 'CAL_HI', 'CNO', 'PERIODIC']


class pGemConditionSummaryParser(pHtmlWriter):
    
    def getMapping(self, conditionSummary):
        mapping = ''
        for (i, bitLabel) in enumerate(BITS_LIST):
            if (conditionSummary >> i) & 0x1 == 1:
                mapping += '%s & ' % bitLabel
        if mapping == '':
            mapping = '-'
        return mapping.strip(' & ')

    def writeTable(self, outputFilePath):
        self.openPage(outputFilePath, 'GEM Condition Summary')
        self.openTable(['Condition summary', 'Mapping to primitives'])
        for i in range(128):
            self.writeTableLine([i, self.getMapping(i)])
        self.closePage()


if __name__ == '__main__':
    parser = pGemConditionSummaryParser()
    parser.writeTable('gem_condition_summary.html')
