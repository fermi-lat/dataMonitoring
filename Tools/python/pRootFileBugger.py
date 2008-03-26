
import ROOT
import sys
import random
import numpy
import logging
logging.basicConfig(level = logging.DEBUG)

from pDataPoint import pDataPoint
from math       import sqrt

TREE_NAME = 'Time'
MET_OFFSET = 978307200000
DELTA_TIME = 15.0
SELECTION_DICT = {
    'Tower': 'tower=%d',
    'TowerCalLayer': 'tower=%d&callayer=%d',
    'TowerCalLayerCalColumn': 'tower=%d&callayer=%d&calcolumn=%d',
    'TowerCalLayerCalColumnCalXFace':\
      'tower=%d&callayer=%d&calcolumn=%d&calxface=%d',
    'TowerCalLayerCalColumnCalXFaceRange':\
      'tower=%d&callayer=%d&calcolumn=%d&calxface=%d&range=%d',
    'TowerPlane': 'tower=%d&plane=%d',
    'TowerPlaneGTFE': 'tower=%d&plane=%d&gtfe=%d',
    'AcdTile': 'acdtile=%d',
    'GARC': 'garc=%d',
    'XYZ': 'xyz=%d',
    'ReconNumTracks': 'reconnumtracks=%d',
    'GammaFilterBit': 'gammafilterbit=%d',
    'TriggerEngine': 'triggerengine=%d'
    }
LABEL_DICT = {
    'fastMon': 'FastMon_Trend_',
    'digi'   : 'Digi_Trend_'   ,
    'recon'  : 'Recon_Trend_'
    }
TREND_TYPE_LIST = ['CounterDiffRate_', 'Counter_', 'Mean_', 'OutF_', 'Rate_']
SUFFIX_LIST = ['err', 'n']
ROOT2NUMPYDICT = {
    'C' : 'c',      #a character string terminated by the 0 char
    'B' : 'int8',   #an 8 bit signed integer (Char_t)
    'b' : 'uint8',  #an 8 bit unsigned integer (UChar_t)
    'S' : 'int16',  #a 16 bit signed integer (Short_t)
    's' : 'uint16', #a 16 bit unsigned integer (UShort_t)
    'I' : 'int32',  #a 32 bit signed integer (Int_t)
    'i' : 'uint32', #a 32 bit unsigned integer (UInt_t)
    'F' : 'float32',#a 32 bit floating point (Float_t)
    'D' : 'float64',#a 64 bit floating point (Double_t)
    'L' : 'int64',  #a 64 bit signed integer (Long64_t)
    'l' : 'uint64'  #a 64 bit unsigned integer (ULong64_t)
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
        self.BranchesTypeDict = {}
        for trendType in TREND_TYPE_LIST:
            self.BranchesTypeDict[trendType] = []
        for i in range(self.RootTree.GetListOfBranches().LastIndex() + 1):
            branchName = self.RootTree.GetListOfBranches().At(i).GetName()
            trendType = '%s_' % branchName.split('_')[0]
            suffix = branchName.split('_')[-1]
            if trendType in TREND_TYPE_LIST and suffix not in SUFFIX_LIST:
                self.BranchesDict[branchName] = self.getBranchDescr(branchName)
                self.BranchesTypeDict[trendType].append(branchName)

    def getBranchDescr(self, branchName):
        title = self.RootTree.GetBranch(branchName).GetTitle()
        type  = title[-1]
        shape = title.replace(branchName, '').split('/')[0]
        if shape == '':
            shape = (1,)
        else:
            shape =\
                  shape.replace('][', ',').replace('[', '(').replace(']', ')')
            if ',' not in shape:
                shape = shape.replace(')', ',)')
            shape = eval(shape)
        return (type, shape)

    def getRandomBranchName(self, trendType = None):
        if trendType == None:
            return random.choice(self.BranchesDict.keys())
        else:
            try:
                return random.choice(self.BranchesTypeDict['%s_' % trendType])
            except:
                return None

    def getRandomIndex(self, branchShape):
        index = []
        for i in branchShape:
            index.append(random.choice(range(i)))
        index = tuple(index)
        logging.debug('Random index from shape %s: %s' % (branchShape, index))
        return index

    def getSelection(self, branchName, index):
        try:
            for (key, value) in SELECTION_DICT.items():
                if key == branchName.split('_')[-1]:
                    return value % index
            return ''
        except TypeError:
            sys.exit('Could not determine selection for branch %s, index %s' %\
                     (branchName, index))

    def getRandomSelection(self, branchName):
        (branchType, branchShape) = self.BranchesDict[branchName]
        return self.getSelection(branchName, self.getRandomIndex(branchShape))

    def getBranchInfo(self, variable):
        branchName = variable.replace(self.Prefix, '')
        (branchType, branchShape) = self.BranchesDict[branchName]
        return '%s: type = %s, shape = %s' % (branchName, branchType,\
                                              branchShape)

    def getTimeBinStart(self, row):
        if row == 0:
            binStart = self.RootTree.Bin_End - self.RootTree.TrueTimeInterval
        elif row == self.RootTree.GetEntriesFast() - 1:
            binStart = self.RootTree.Bin_Start
        else:
            binStart = self.RootTree.Bin_Start
        return binStart

    def getTimeBinEnd(self, row):
        if row == 0:
            binEnd = self.RootTree.Bin_End
        elif row == self.RootTree.GetEntriesFast() - 1:
            binEnd = self.RootTree.Bin_Start + self.RootTree.TrueTimeInterval
        else:
            binEnd = self.RootTree.Bin_End
        return binEnd

    def getTimeBinCenter(self, row):
        binStart = int(self.getTimeBinStart(row)*1000 + MET_OFFSET)
        binEnd = int(self.getTimeBinEnd(row)*1000 + MET_OFFSET)
        return (binStart + binEnd)/2

    def getTimeBinWidth(self, row):
        return (self.getTimeBinEnd(row) - self.getTimeBinStart(row))

    def getDataPoints(self, variable, selection):
        branchName = variable.replace(self.Prefix, '')
        (branchType, branchShape) = self.BranchesDict[branchName]
        self.VarArray = numpy.zeros(branchShape, ROOT2NUMPYDICT[branchType])
        self.ErrArray = numpy.zeros(branchShape, ROOT2NUMPYDICT[branchType])
        self.RootTree.SetBranchAddress(branchName, self.VarArray)
        if not ('Counter_' in variable):
            self.RootTree.SetBranchAddress('%s_err' % branchName,self.ErrArray)
        if selection != '':
            indexString = ''
            for item in selection.split('&'):
                indexString += '[%s]' % item.split('=')[1].strip()
        else:
            indexString = '[0]'
        dataPoints = []
        for i in range(self.RootTree.GetEntriesFast()):
            self.RootTree.GetEntry(i)
            time = self.getTimeBinCenter(i)
            timeBinWidth = self.getTimeBinWidth(i)        
            value = eval('self.VarArray%s' % indexString)
            error = eval('self.ErrArray%s' % indexString)
            dataPoints.append(pDataPoint(time, value, error))
        self.RootTree.ResetBranchAddresses()
        return dataPoints
            


if __name__ == '__main__':
    bugger = pRootFileBugger('../trending/chuncks/r0258292096_digiTrend.root')
    print bugger.getDataPoints('Digi_Trend_Mean_AcdPha_PmtB_AcdTile',\
                                   'acdtile=23')
