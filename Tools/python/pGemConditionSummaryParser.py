
from pHtmlWriter import *


BITS_LIST = ['ROI', 'TKR', 'CAL_LO', 'CAL_HI', 'CNO', 'PERIODIC']
TITLE = 'GEM Condition Summary'


class pGemConditionSummaryParser(pHtmlWriter):
    
    def getLabel(self, conditionSummary):
        label = ''
        for (i, bitLabel) in enumerate(BITS_LIST):
            if (conditionSummary >> i) & 0x1 == 1:
                label += '%s & ' % bitLabel
        if label == '':
            label = '-'
        return label.strip(' & ')

    def writeTable(self, outputFilePath):
        self.openPage(outputFilePath)
        self.writePageHead(TITLE, '%s/css/glastCommons.jsp' % COMMONS_PATH)
        self.openBody(False)
        self.openDiv({'class': 'pageBody'})
        self.openTag('p')
        self.openTag('img',\
             {'src': '%s/logoServlet.jsp?title=%s' % (COMMONS_PATH, TITLE)},\
                         None, True)
        self.closeTag()
        self.openTag('b')
        self.closeTag()
        self.openTag('table', {'class': 'datatable'})
        self.openTag('thead')
        self.openTag('tr')
        for text in ['Condition Summary', 'Explanation']:
            self.openTag('th', {}, text, True)
        self.closeTag()
        self.closeTag()
        self.openTag('tbody')
        for i in range(128):
            if i%2 == 1:
                className = 'even'
            else:
                className = 'odd'
            self.openTag('tr', {'class': className})
            label = self.getLabel(i)
            for text in [str(i), label]:
                self.openTag('td', {'class': 'leftAligned'}, text, True)
            self.closeTag()
        self.closePage()



if __name__ == '__main__':
    parser = pGemConditionSummaryParser()
    parser.writeTable('gem_condition_summary.html')
