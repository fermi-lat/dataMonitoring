
from pHtmlWriter import *


BITS_LIST = ['ROI', 'TKR', 'CAL_LO', 'CAL_HI', 'CNO', 'PERIODIC',\
                 'SOLICITED', 'EXTERNAL']
FORMATTED_BITS_LIST = ''
for (bit, label) in enumerate(BITS_LIST):
    FORMATTED_BITS_LIST += 'bit %d (decimal %d): %s<br/>' %\
        (bit, 2**bit, label)
MAIN_TEXT =\
"""
The following table maps the (decimal) values of the GEMcondition
summary register to the actual physical content in terms of trigger
primitives.<br/>

The GEM condition summary is a 8-bit register mapping the trigger primitives
in the following order:
<div class=exampleCode>
%s
</div>
<p>All the combinations of the first 6 bits (which are the most useful) are
explicitely listed in the table.</p>
""" % FORMATTED_BITS_LIST

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
        self.addParagraph(MAIN_TEXT)
        self.openTable(['Condition summary', 'Mapping to primitives'])
        for i in range(64):
            self.writeTableLine([i, self.getMapping(i)])
        self.closePage()


if __name__ == '__main__':
    parser = pGemConditionSummaryParser()
    parser.writeTable('gem_condition_summary.html')
