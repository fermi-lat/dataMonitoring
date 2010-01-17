
from pMeritTrendProcessor import *


NOT_ROCK_ANGLE_CUT = '!(%s)' % ROCK_ANGLE_CUT
FIT_FUNCTION = ROOT.TF1('fitFunc', 'pol3', 0, 100)
NUM_FIT_PARS = FIT_FUNCTION.GetNpar()
FIT_FUNCTION.SetLineColor(ROOT.kRed)


class pMeritTrendPostProcessor(pMeritTrendProcessor):

    def __init__(self, filePath, treeName = 'Time'):
        self.RootFile = ROOT.TFile(filePath)
        self.RootTree = self.RootFile.Get(treeName)
        self.GraphDict = {}
        self.FitParamDict = {}
        self.FitErrorDict = {}
        self.RateHistDict = {}
        self.__retrieveRateHists()

    def __retrieveRateHists(self):
        for varName in VARIABLE_LIST:
            varLength = VARIABLE_DICT[varName][0]
            if varLength == 1:
                hName = self.getHistName(varName)
                self.RateHistDict[hName] = self.RootFile.Get(hName)
            else:
                for i in range(varLength):
                    hName = self.getHistName(varName, i)
                    self.RateHistDict[hName] = self.RootFile.Get(hName)

    def resetFitFunction(self):
        for i in range(NUM_FIT_PARS):
            FIT_FUNCTION.SetParameter(i, 0.0)
            FIT_FUNCTION.SetParError(i, 1.0)
        FIT_FUNCTION.SetParameter(1, 1.0)

    def getGraphName(self, varName, index = None):
        if index is None:
            return 'g%s' % varName
        else:
            return 'g%s_%d' % (varName, index)

    def getEarthLimbCorrection(self, varName, index = None):
        gName = self.getGraphName(varName, index)
        params = self.FitParamDict[gName]
        errors = self.FitErrorDict[gName]
        numPars = len(params)
        text = '\nEarth limb correction fit parameters   :  %d' % numPars
        for i in range(numPars):
            text += '\np%d :  %.4e+/-%.4e' % (i, params[i], errors[i])
        return text

    def drawGraph(self, varName, index = None, interactive = True):
        if index is None:
            self.RootTree.Draw('%s:Mean_PtSCzenith' % varName,
                               NOT_ROCK_ANGLE_CUT)
            gName = self.getGraphName(varName)
        else:
            self.RootTree.Draw('%s[%d]:Mean_PtSCzenith' % (varName, index),
                               NOT_ROCK_ANGLE_CUT)
            gName = self.getGraphName(varName, index)
        g = self.GraphCanvas.GetPrimitive('Graph')
        g.SetName(gName)
        g.SetMarkerStyle(26)
        g.SetMarkerSize(0.3)
        self.resetFitFunction()
        g.Fit('fitFunc', 'Q')
        params = [FIT_FUNCTION.GetParameter(i) for i in range(NUM_FIT_PARS)]
        errors = [FIT_FUNCTION.GetParError(i) for i in range(NUM_FIT_PARS)]
        self.FitParamDict[gName] = params
        self.FitErrorDict[gName] = errors
        print '*** Variable %s %s' %\
            (varName, ('(index = %s)' % index)*(index is not None))
        for i in range(NUM_FIT_PARS):
            print 'p_%d = %.3e +- %.3e' % (i, params[i], errors[i])
        print 'Value @ 50 degrees: %.3f\n' % FIT_FUNCTION.Eval(50)
        self.GraphCanvas.Update()
        if interactive:
            raw_input('Press enter to continue.')

    def process(self, interactive = True):
        print 'Post-processing file...'
        self.GraphCanvas = ROOT.TCanvas('Graph canvas')
        self.GraphCanvas.SetGridx(True)
        self.GraphCanvas.SetGridy(True)
        cut = '!(%s)' % (ROCK_ANGLE_CUT)
        for varName in VARIABLE_LIST:
            varLength = VARIABLE_DICT[varName][0]
            if varLength == 1:
                self.drawGraph(varName, None, interactive)
            else:
                for i in range(varLength):
                    self.drawGraph(varName, i, interactive)
        print 'Done.'



if __name__ == '__main__':
    p = pMeritTrendPostProcessor('normrates/merit_norm_proc.root')
    p.process(interactive = False)
    p.writeConfigFile('normrates/merit_norm_postproc.txt')
        
