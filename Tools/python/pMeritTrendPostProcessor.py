
from pMeritTrendProcessor import *


NOT_ROCK_ANGLE_CUT = '!(%s)' % ROCK_ANGLE_CUT
FIT_FORMULA  = 'pol3'


class pMeritTrendPostProcessor(pMeritTrendProcessor):

    def __init__(self, filePath, treeName = 'Time'):
        self.RootFile = ROOT.TFile(filePath)
        self.RootTree = self.RootFile.Get(treeName)
        self.GraphDict = {}
        self.FitFuncDict = {}
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

    def getGraphName(self, varName, index = None):
        if index is None:
            return 'g%s' % varName
        else:
            return 'g%s_%d' % (varName, index)

    def getFuncName(self, varName, index = None):
        return 'fit_%s' % self.getGraphName(varName, index)

    def getEarthLimbCorrection(self, varName, index = None):
        gName = self.getGraphName(varName, index)
        params = self.FitParamDict[gName]
        errors = self.FitErrorDict[gName]
        numPars = len(params)
        text = '\nEarthLimbCorr : %d' % numPars
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
        fName = self.getFuncName(varName, index)
        f = ROOT.TF1(fName, FIT_FORMULA, 0, 105)
        f.SetLineColor(ROOT.kRed)
        numFitPars = f.GetNpar()
        self.FitFuncDict[fName] = f
        g.Fit(fName, 'Q')
        # If the value at 50 degree rocking is too far from 1, disengage the
        # correction, i.e. set all parameters to zero except for the constant
        # term (which is set to one).
        if abs(f.Eval(50) - 1.0) > 0.1:
            print 'Disengaging correction for the Earth limb in the FOV.'
            for i in range(numFitPars):
                f.SetParameter(i, 0.0)
                f.SetParError(i, 0.0)
            f.SetParameter(0, 1.0)
        params = [f.GetParameter(i) for i in range(numFitPars)]
        errors = [f.GetParError(i) for i in range(numFitPars)]
        self.FitParamDict[gName] = params
        self.FitErrorDict[gName] = errors
        print '*** Variable %s %s' %\
            (varName, ('(index = %s)' % index)*(index is not None))
        for i in range(numFitPars):
            print 'p_%d = %.3e +- %.3e' % (i, params[i], errors[i])
        print 'Value @ 50 degrees: %.3f\n' % f.Eval(50)
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

    def copyArrays(self):
        rockAngle = self.InputArrayDict['Mean_PtSCzenith'][0]
        for (name, (length, type)) in VARIABLE_DICT.items():
            if name not in VARIABLE_LIST:
                self.OutputArrayDict[name][0] = self.InputArrayDict[name][0]
            elif length == 1:
                f = self.FitFuncDict[self.getFuncName(name)]
                norm = f.Eval(rockAngle)
                if norm == 0:
                    norm = 1
                self.OutputArrayDict[name][0] =\
                    self.InputArrayDict[name][0]/norm
            else:
                for i in range(length):
                    f = self.FitFuncDict[self.getFuncName(name, i)]
                    norm = f.Eval(rockAngle)
                    if norm == 0:
                        norm = 1
                    self.OutputArrayDict[name][i] =\
                        self.InputArrayDict[name][i]/norm



if __name__ == '__main__':
    p = pMeritTrendPostProcessor('normrates/merit_norm_proc.root')
    p.process(interactive = False)
    p.writeRootFile('normrates/merit_norm_postproc.root')
    p.writeConfigFile('normrates/FactorsToNormRates_EarthLimb.txt')
