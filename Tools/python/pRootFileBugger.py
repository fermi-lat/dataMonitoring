
import ROOT
import sys
import random
import logging
logging.basicConfig(level = logging.DEBUG)

from pDataPoint import pDataPoint

TREE_NAME = 'Time'
MET_OFFSET = 978307200000
SELECTION_DICT = {'Tower':\
                      'tower=%d',
                  'TowerCalLayer':\
                      'tower=%d&callayer=%d',
                  'TowerCalLayerCalColumn':\
                      'tower=%d&callayer=%d&calcolumn=%d',
                  'TowerCalLayerCalColumnCalXFace':\
                      'tower=%d&callayer=%d&calcolumn=%d&calxface=%d',
                  'TowerCalLayerCalColumnCalXFaceRange':\
                      'tower=%d&callayer=%d&calcolumn=%d&calxface=%d&range=%d',
                  'TowerPlane':\
                      'tower=%d&plane=%d',
                  'TowerPlaneGTFE':\
                      'tower=%d&plane=%d&gtfe=%d',
                  'AcdTile':\
                      'acdtile=%d',
                  'GARC':\
                      'garc=%d',
                  'XYZ':\
                      'xyz=%d',
                  'ReconNumTracks':\
                      'reconnumtracks=%d',
                  'GammaFilterBit':\
                      'gammafilterbit=%d',
                  'TriggerEngine':\
                      'triggerengine=%d'
                  }
LABEL_DICT = {'fastMon': 'FastMon_Trend_',
              'digi'   : 'Digi_Trend_'   ,
              'recon'  : 'Recon_Trend_'
              }


class pRootFileBugger:
    
    def __init__(self, filePath):
        self.Type = None
        for (key, value) in LABEL_DICT.items():
            if key in filePath:
                self.Type = key
                self.Prefix = value
        if self.Type is None:
            logging.error('The filename must contain "%s", "%s" or "%s".' %\
                              tuple(LABEL_DICT.keys()))
            sys.exit('Abort.')
        logging.debug('Opening %s...' % filePath)
        self.RootFile = ROOT.TFile(filePath)
        if self.RootFile.IsZombie():
            sys.exit('Could not open %s.' % filePath)
        logging.debug('Retrieving the ROOT tree...')
        self.RootTree = self.RootFile.Get(TREE_NAME)
        self.__fillBranchesDict()

    def __fillBranchesDict(self):
        self.BranchesDict = {}
        for i in range(self.RootTree.GetListOfBranches().LastIndex() + 1):
            branchName = self.RootTree.GetListOfBranches().At(i).GetName()
            self.BranchesDict[branchName] = self.getBranchShape(branchName)

    def getBranchShape(self, branchName):
        title = self.RootTree.GetBranch(branchName).GetTitle()
        shape = title.replace(branchName, '').split('/')[0]
        if shape == '':
            shape = (1,)
        else:
            shape = shape.replace('][', ',').replace('[', '(').replace(']', ')')
            if ',' not in shape:
                shape = shape.replace(')', ',)')
            shape = eval(shape)
        return shape

    def getRandomBranchName(self):
        return random.choice(self.BranchesDict.keys())

    def getRandomIndex(self, branchName):
        index = []
        for i in self.getBranchShape(branchName):
            index.append(random.choice(range(i)))
        return tuple(index)

    def getSelection(self, branchName, index):
        for (key, value) in SELECTION_DICT.items():
            if key in branchName:
                return value % index
        return ''

    def getRandomSelection(self, branchName):
        return self.getSelection(branchName, self.getRandomIndex(branchName))

    def getDataPoints(self, variable, selection):
        variable = variable.replace(self.Prefix, '')
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
