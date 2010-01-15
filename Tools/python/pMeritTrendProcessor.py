
import math
import array

from pSafeROOT         import ROOT
from pMeritTrendMerger import VARIABLE_DICT

ROCK_ANGLE_CUT = 'abs(Mean_PtSCzenith - 50) < 0.2'
MIN_L = 0.9
MAX_L = 1.9
NUM_BINS_L = 200
"""
VARIABLE_LIST = ['Rate_EvtsBeforeCuts',
                 'Rate_EvtsBeforeCutsWithGAMMAFilter',
                 'Rate_TransientEvts',
                 'Rate_DiffuseEvts',
                 'Rate_SourceEvts',
                 'CounterDiffRate_EvtsBeforeFilters',
                 'Rate_MeritTriggerEngine',
                 'Rate_GAMMAFilterAndTriggerEngine']
"""
VARIABLE_LIST = ['Rate_EvtsBeforeCuts']



class pMeritTrendProcessor:

    def __init__(self, filePath = 'merittrend.root', treeName = 'Output'):
        self.RootFile = ROOT.TFile(filePath)
        self.RootTree = self.RootFile.Get(treeName)
        self.McIlwainLHist = ROOT.TH1F('McIlwainL', 'McIlwainL',
                                       NUM_BINS_L, MIN_L, MAX_L)
        self.RootTree.Project('McIlwainL', 'Mean_PtMcIlwainL', ROCK_ANGLE_CUT)
        self.RateHistDict = {}
        self.SlopeGraphDict = {}
        self.process()

    def createRateHist(self, hName, cut):
        print 'Creating hist %s...' % hName
        h = ROOT.TH1F(hName, hName, NUM_BINS_L, MIN_L, MAX_L)
        self.RootTree.Project(hName, 'Mean_PtMcIlwainL', cut)
        self.RateHistDict[hName] = h
        h.Divide(self.McIlwainLHist)
        return h

    def getHistName(self, varName, index = None):
        if index is None:
            return 'h%s' % varName
        else:
            return 'h%s_%d' % (varName, index)
        
    def createRateHists(self):
        for varName in VARIABLE_LIST:
            varLength = VARIABLE_DICT[varName][0]
            if varLength == 1:
                cut = '(%s)*%s' % (ROCK_ANGLE_CUT, varName)
                self.createRateHist(self.getHistName(varName), cut)
            else:
                for i in range(varLength):
                    cut = '(%s)*%s[%d]' % (ROCK_ANGLE_CUT, varName, i)
                    self.createRateHist(self.getHistName(varName, i), cut)
                    
    def process(self):
        self.createRateHists()

    def getRate(self, mcIlwainL, varName, index = None):
        hName = self.getHistName(varName, index)
        h = self.RateHistDict[hName]
        bin = int(NUM_BINS_L*(mcIlwainL - MIN_L)/(MAX_L - MIN_L)) + 1
        return (h.GetBinContent(bin), h.GetBinError(bin))

    def drawRateHists(self):
        self.RateCanvasDict = {}
        for (hName, h) in self.RateHistDict.items():
            cName = '%s_canvas' % hName
            self.RateCanvasDict[cName] = ROOT.TCanvas(cName, cName)
            h.Draw()

    def createArrays(self):
        print 'Creating arrays...'
        self.InputArrayDict  = {}
        self.OutputArrayDict = {}
        for (name, (length, type)) in VARIABLE_DICT.items():
            self.InputArrayDict[name] = array.array(type.lower(), [0.]*length)
            self.OutputArrayDict[name] = array.array(type.lower(), [0.]*length)
            suffix = '/%s' % type
            if length > 1:
                suffix = '[%d]%s' % (length, type)
            self.OutputTree.Branch(name, self.OutputArrayDict[name],
                                   '%s%s' % (name, suffix))
            self.RootTree.SetBranchAddress(name, self.InputArrayDict[name])
        print 'Done.'

    def copyArrays(self):
        mcIlwainL = self.InputArrayDict['Mean_PtMcIlwainL'][0]
        for (name, (length, type)) in VARIABLE_DICT.items():
            if name not in VARIABLE_LIST:
                self.OutputArrayDict[name][0] = self.InputArrayDict[name][0]
            elif length == 1:
                (norm, err) = self.getRate(mcIlwainL, name)
                if norm == 0:
                    norm = 1
                self.OutputArrayDict[name][0] =\
                    self.InputArrayDict[name][0]/norm
            else:
                for i in range(length):
                    (norm, err) = self.getRate(mcIlwainL, name, i)
                    if norm == 0:
                        norm = 1
                    self.OutputArrayDict[name][i] =\
                        self.InputArrayDict[name][i]/norm

    def write(self, outputFilePath):
        self.OutputFile = ROOT.TFile(outputFilePath, 'RECREATE')
        self.OutputTree = ROOT.TTree('Output', 'Output')
        self.createArrays()
        print 'Writing output file...'
        numEntries = self.RootTree.GetEntries()
        for i in xrange(numEntries):
            self.RootTree.GetEntry(i)
            self.copyArrays()
            self.OutputTree.Fill()
        self.OutputFile.cd()
        self.OutputTree.Write()
        self.OutputFile.Close()
        print 'Done.'
        


if __name__ == '__main__':
    p = pMeritTrendProcessor()
    p.drawRateHists()
    p.write('merittrend_proc.root')
    
