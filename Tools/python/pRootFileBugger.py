
import ROOT
import sys
import logging
logging.basicConfig(level = logging.DEBUG)

from pDataPoint import pDataPoint

TREE_NAME = 'Time'
MET_OFFSET = 978307200000


class pRootFileBugger:
    
    def __init__(self, filePath):
        logging.debug('Opening %s...' % filePath)
        self.RootFile = ROOT.TFile(filePath)
        if self.RootFile.IsZombie():
            sys.exit('Could not open %s.' % filePath)
        logging.debug('Retrieving the ROOT tree...')
        self.RootTree = self.RootFile.Get(TREE_NAME)          

    def getDataPoints(self, variable, selection):
        variable = variable.replace('FastMon_Trend_', '')
        variable = variable.replace('Digi_Trend_', '')
        variable = variable.replace('Recon_Trend_', '')
        dataPoints = []
        indexString = ''
        if selection != '':
            for item in selection.split(','):
                indexString += '[%s]' % item.split('=')[1].strip()
        for i in range(self.RootTree.GetEntriesFast()):
            self.RootTree.GetEntry(i)
            if i != self.RootTree.GetEntriesFast() - 1:
                time = self.RootTree.Bin_End -\
                    self.RootTree.TrueTimeInterval/2.
            else:
                time = self.RootTree.Bin_Start +\
                    self.RootTree.TrueTimeInterval/2.
            time = time*1000 + MET_OFFSET
            value = eval('self.RootTree.%s%s' % (variable, indexString))
            error = eval('self.RootTree.%s_err%s' % (variable, indexString))
            dataPoints.append(pDataPoint(time, value, error))
        return dataPoints
            


if __name__ == '__main__':
    bugger = pRootFileBugger('../trending/chuncks/r0258292096_digiTrend.root')
    print bugger.getDataPoints('Digi_Trend_Mean_AcdPha_PmtB_AcdTile',\
                                   'acdtile=23')
