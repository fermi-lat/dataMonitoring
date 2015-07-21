
import math
import array
import os

from pSafeROOT         import ROOT
from pMeritTrendMerger import VARIABLE_DICT

ROCK_ANGLE_CUT = 'abs(abs(Mean_PtSCzenith) - 50) < 0.2'
MIN_L = 0.9
MAX_L = 1.9
NUM_BINS_L = 200
MIN_VALID_BINS_L = 1


VARIABLE_LIST = [
    # Events before cuts/filters
    'Rate_EvtsBeforeCuts',
    'Rate_EvtsBeforeCutsWithGAMMAFilter',
    'CounterDiffRate_EvtsBeforeFilters',
    # Trigger engines
    'Rate_MeritTriggerEngine',
    'Rate_GAMMAFilterAndTriggerEngine',
    # Photon classes: transient...
    'Rate_TransientEvts',
    'Rate_TransientEvtsBelowZenithTheta100',
    # ... source ...
    'Rate_SourceEvts',
    'Rate_SourceEvtsBelowZenithTheta100',
    # ... clean ...
    'Rate_CleanEvts',
    'Rate_CleanEvtsBelowZenithTheta100',
    # ... and ultraclean
    'Rate_UltraCleanEvts',
    'Rate_UltraCleanEvtsBelowZenithTheta100',
    # LLE events
    'Rate_LLEEvts'
    ]


VARIABLE_ERR_LIST = []
for varName in VARIABLE_LIST:
    VARIABLE_ERR_LIST.append('%s_err' % varName)


CONFIG_FILE_PREAMBLE =\
"""# File containing the Normalization factors for several rates
# -------------------------------------------------------------
#

"""

VARIABLE_PREAMBLE =\
"""RateName   :  %s
Computation of Normalization factors   :  %s
RefRateVal :  %s+/-%s%s
Start Table:  Mean_PtMcIlwainL_LowEdge	Mean_PtMcIlwainL_UpperEdge	NormFactor	NormFactor_err
"""


class pMeritTrendProcessor:

    def __init__(self, filePath, treeName = 'Time'):
        self.RootFile = ROOT.TFile(filePath)
        self.RootTree = self.RootFile.Get(treeName)
        self.McIlwainLHist = ROOT.TH1F('McIlwainL', 'McIlwainL',
                                       NUM_BINS_L, MIN_L, MAX_L)
        self.RootTree.Project('McIlwainL', 'Mean_PtMcIlwainL', ROCK_ANGLE_CUT)
        self.RateHistDict   = {}
        self.LimbFuncDict   = {}
        self.LonFuncDict    = {}
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

    def getHist(self, varName, index = None):
        return self.RateHistDict[self.getHistName(varName, index)]
        
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
        varName = varName.replace('_err', '')
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
            self.InputArrayDict[name] = array.array(type.lower(), [0]*length)
            self.OutputArrayDict[name] = array.array(type.lower(), [0]*length)
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
            if name not in VARIABLE_LIST and name not in VARIABLE_ERR_LIST:
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

    def writeRootFile(self, filePath):
        outputFile = ROOT.TFile(filePath, 'RECREATE')
        self.OutputTree = ROOT.TTree('Time', 'Time')
        self.createArrays()
        print 'Writing output root file %s...' % filePath
        print 'Writing processed tree...'
        numEntries = self.RootTree.GetEntries()
        for i in xrange(numEntries):
            self.RootTree.GetEntry(i)
            self.copyArrays()
            self.OutputTree.Fill()
        outputFile.cd()
        self.OutputTree.Write()
        print 'Writing histograms...'
        for h in self.RateHistDict.values():
            h.Write()
        for f in self.LimbFuncDict.values():
            f.Write()
        for f in self.LonFuncDict.values():
            f.Write()
        outputFile.Close()
        print 'Done.'

    def getFullCorrection(self, varName, index = None):
        return ''

    def formatNumber(self, number, numDecPlaces):
        formatString = '%%.%df' % numDecPlaces
        return (formatString % number).rstrip('0').rstrip('.')
    
    #filling empty histogram bins, looking for the closer bin !=0, in the 5 bins around
    def fillEmptyBins(self,h,  binErrorCorr,   binContentCorr):
           numBins=h.GetNbinsX()
           nRange=6 #max dbin distance between the empty bin and the one used.
           for i in range(1, numBins + 1):
               if (h.GetBinContent(i)==0):
                   binIndexDiff_left=100
                   binIndexDiff_right=100
                   binIndexDiff=0
                   for jj in range(1,nRange):
                       if (i-jj)>1 and  i+jj<numBins+1:
                           if (h.GetBinContent(i-jj)!=0):
                               binIndexDiff_left=jj
                               break
                   for jj in range(1,nRange):
                       if (i-jj)>1 and  i+jj<numBins+1:
                           if  h.GetBinContent(i+jj)!=0:
                               binIndexDiff_right=jj
                               break
                   if  not(binIndexDiff_left==100 and binIndexDiff_right==100):
                        if  binIndexDiff_left<binIndexDiff_right:
                            binIndexDiff=-binIndexDiff_left
                        else:   
                            binIndexDiff=binIndexDiff_right
                   
                   binContentCorr[i]= h.GetBinContent(i+binIndexDiff)
                   binErrorCorr[i]= h.GetBinError(i+binIndexDiff) 
                            
                   #in case of 1 bin hole, fill with the average
                   if (i-1)>1 and  i+1<numBins+1:
                       if ( h.GetBinContent(i-1)!=0 and  h.GetBinContent(i+1)!=0):
                           binContentCorr[i]=(h.GetBinContent(i-1)+ h.GetBinContent(i+1))/2.
                           binErrorCorr[i]= 0.5*math.sqrt((h.GetBinError(i-1)**2) +(h.GetBinError(i+1)**2))


    def getHistAsText(self, varName, index = None):
        h = self.getHist(varName, index)
        numBins = h.GetNbinsX()
        sy  = 0.0
        syy = 0.0
        n   = 0
        for i in range(1, numBins + 1):
            binContent = h.GetBinContent(i)
            if binContent > 0:
                sy  += binContent
                syy += binContent*binContent
                n   += 1
        if n >= MIN_VALID_BINS_L:
            yMean = sy/n
            yMeanRms = math.sqrt((syy/n - yMean*yMean)/n)
            status = 'Successful'
            yMeanText = '%.4e' % yMean
            yMeanRmsText = '%.4e' % yMeanRms
        else:
            yMean = -1
            yMeanRms = -1
            status = 'NOT-Successful'
            yMeanText = '-1'
            yMeanRmsText = '-1'
        print '- %s %s: valid bins = %d, %s.' %\
            (varName, ('(index = %s)' % index)*(index is not None), n, status)
        compVarName = '%s%s' % (varName, ('[%s]' % index)*(index is not None))
        text = VARIABLE_PREAMBLE %\
               (compVarName, status, yMeanText, yMeanRmsText,
                self.getFullCorrection(varName, index))

        ######### empty bins correction
        binErrorCorr=[0.]* (numBins+1)
        binContentCorr=[0.]* (numBins+1)
        self.fillEmptyBins(h,  binErrorCorr,   binContentCorr)

        for i in range(1, numBins + 1):
            loEdge = h.GetBinLowEdge(i)
            hiEdge = loEdge + h.GetBinWidth(i)
            binContent = h.GetBinContent(i)
            binError = h.GetBinError(i)
            #empty bin correction
            if binContent==0: 
                binContent=binContentCorr[i]
                binError=binErrorCorr[i]      

            if yMean > 0:
                binContent /= yMean
                binError   /= yMean
            else:
                binContent = 0
                binError   = 0
            text += '%s\t\t%s\t\t%s\t\t%s\n' %\
                (self.formatNumber(loEdge, 3),
                 self.formatNumber(hiEdge, 3),
                 self.formatNumber(binContent, 6),
                 self.formatNumber(binError, 6))
        text += 'End Table\n\n'
        return text
        
    def writeConfigFile(self, filePath):
        print 'Writing output config file %s...' % filePath
        outputFile = file(filePath, 'w')
        outputFile.writelines(CONFIG_FILE_PREAMBLE)
        for varName in VARIABLE_LIST:
            varLength = VARIABLE_DICT[varName][0]
            if varLength == 1:
                outputFile.writelines(self.getHistAsText(varName))
            else:
                for i in range(varLength):
                    outputFile.writelines(self.getHistAsText(varName, i))
        outputFile.close()
        print 'Done.'
        


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] rootFilePath')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    rootFilePath = args[0]
    if not rootFilePath.endswith('.root'):
        parser.print_help()
        parser.error('Please give an input root file.')
    p = pMeritTrendProcessor(rootFilePath)
    p.drawRateHists()
    outputRootFilePath = rootFilePath.replace('.root', '_proc.root')
    outputFolder = os.path.dirname(rootFilePath)
    outputTextFilePath = os.path.join(outputFolder,
                                      'FactorsToNormRates_noEarthLimb.txt')
    p.writeRootFile(outputRootFilePath)
    p.writeConfigFile(outputTextFilePath)
