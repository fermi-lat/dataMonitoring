
from pMeritTrendProcessor import *


NOT_ROCK_ANGLE_CUT = '!(%s)' % ROCK_ANGLE_CUT
MIN_NORM_RATE    = 0.3
LIMB_FIT_FORMULA = '[0] + [1]*(x>[3])*(x-[3]) + [2]*(x>[3])*(x-[3])**2'
MIN_ROCK_ANGLE   = 0
LIMB_ROCK_ANGLE  = 35
MAX_ROCK_ANGLE   = 95
LON_FIT_FORMULA  = 'min(1, 1 - [0] + [0]*abs([2]*(x - [1])))'


class pMeritTrendPostProcessor(pMeritTrendProcessor):

    def __init__(self, filePath, treeName = 'Time'):
        self.RootFile = ROOT.TFile(filePath)
        self.RootTree = self.RootFile.Get(treeName)
        self.RateHistDict = {}
        self.LimbFuncDict = {}
        self.LimbParamDict = {}
        self.LimbErrorDict = {}
        self.LonFuncDict = {}
        self.LonParamDict = {}
        self.LonErrorDict = {}
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

    def getLimbGraphName(self, varName, index = None):
        if index is None:
            return 'gLimb%s' % varName
        else:
            return 'gLimb%s_%d' % (varName, index)

    def getLimbFuncName(self, varName, index = None):
        return 'fLimb_%s' % self.getLimbGraphName(varName, index)

    def getLonGraphName(self, varName, index = None):
        if index is None:
            return 'gLon%s' % varName
        else:
            return 'gLon%s_%d' % (varName, index)

    def getLonFuncName(self, varName, index = None):
        return 'fLon_%s' % self.getLonGraphName(varName, index)

    def getEarthLimbCorrection(self, varName, index = None):
        gName = self.getLimbGraphName(varName, index)
        params = self.LimbParamDict[gName]
        errors = self.LimbErrorDict[gName]
        numPars = len(params)
        text = '\nEarthLimbCorr (%s): %d' % (LIMB_FIT_FORMULA, numPars)
        for i in range(numPars):
            text += '\np%d :  %.4e+/-%.4e' % (i, params[i], errors[i])
        return text

    def getLongitudeCorrection(self, varName, index = None):
        gName = self.getLonGraphName(varName, index)
        params = self.LonParamDict[gName]
        errors = self.LonErrorDict[gName]
        numPars = len(params)
        text = '\nLongitudeCorr (%s): %d' % (LON_FIT_FORMULA, numPars)
        for i in range(numPars):
            text += '\np%d :  %.4e+/-%.4e' % (i, params[i], errors[i])
        return text

    def getFullCorrection(self, varName, index = None):
        return '%s%s' % (self.getEarthLimbCorrection(varName, index),
                         self.getLongitudeCorrection(varName, index))

    def drawGraph(self, varName, index = None, interactive = True):
        #
        # Correction for the Earth limb in the field of view.
        #
        limbSucceded = True
        fName = self.getLimbFuncName(varName, index)
        f = ROOT.TF1(fName, LIMB_FIT_FORMULA, MIN_ROCK_ANGLE, MAX_ROCK_ANGLE)
        self.LimbFuncDict[fName] = f
        f.FixParameter(3, LIMB_ROCK_ANGLE)
        f.SetLineColor(ROOT.kRed)
        numFitPars = f.GetNpar()
        if index is None:
            cut = '%s > %.3f && %s' %\
                (varName, MIN_NORM_RATE, NOT_ROCK_ANGLE_CUT)
            expr = '%s:Mean_PtSCzenith' % varName
            gName = self.getLimbGraphName(varName)
        else:
            cut = '%s[%d] > %.3f && %s' %\
                (varName, index, MIN_NORM_RATE, NOT_ROCK_ANGLE_CUT)
            print cut
            expr = '%s[%d]:Mean_PtSCzenith' % (varName, index)
            gName = self.getLimbGraphName(varName, index)
        self.RootTree.Draw(expr, cut)
        g = self.GraphCanvas.GetPrimitive('Graph')
        try:
            g.SetName(gName)
            g.SetMarkerStyle(26)
            g.SetMarkerSize(0.3)
            h = ROOT.TH2D('h', 'h', 50, MIN_ROCK_ANGLE, MAX_ROCK_ANGLE,
                          500, 0, 20)
            self.RootTree.Project('h', expr, cut)
            p = h.ProfileX()
            p.SetLineColor(ROOT.kBlue)
            p.SetLineWidth(2)
            p.Draw('same')
            p.Fit(fName, 'QRN')
            f.Draw('same')
            # If the value at 50 degree rocking is too far from 1, disengage the
            # correction, i.e. set all parameters to zero except for the
            # constant term (which is set to one).
            if abs(f.Eval(50) - 1.0) > 0.2:
                print 'Disengaging correction for the Earth limb in the FOV.'
                limbSucceded = False
                for i in range(numFitPars):
                    f.SetParameter(i, 0.0)
                    f.SetParError(i, 0.0)
                f.SetParameter(0, 1.0)
            params = [f.GetParameter(i) for i in range(numFitPars)]
            errors = [f.GetParError(i) for i in range(numFitPars)]
            self.LimbParamDict[gName] = params
            self.LimbErrorDict[gName] = errors
            print '*** Variable %s %s' %\
                (varName, ('(index = %s)' % index)*(index is not None))
            for i in range(numFitPars):
                print 'p_%d = %.3e +- %.3e' % (i, params[i], errors[i])
            print 'Value @ 50 degrees: %.3f\n' % f.Eval(50)
        except:
            print 'Procedure failed for %s.' % gName
            limbSucceded = False
            for i in range(numFitPars):
                f.SetParameter(i, 0.0)
                f.SetParError(i, 0.0)
            f.SetParameter(0, 1.0)
            params = [f.GetParameter(i) for i in range(numFitPars)]
            errors = [f.GetParError(i) for i in range(numFitPars)]
            self.LimbParamDict[gName] = params
            self.LimbErrorDict[gName] = errors
            print '*** Variable %s %s' %\
                (varName, ('(index = %s)' % index)*(index is not None))
            for i in range(numFitPars):
                print 'p_%d = %.3e +- %.3e' % (i, params[i], errors[i])
            print 'Value @ 50 degrees: %.3f\n' % f.Eval(50)
        self.GraphCanvas.Update()
        if interactive:
            raw_input('Press enter to continue.')
        #
        # Correcttion for the longitude effect.
        #
        fName = self.getLonFuncName(varName, index)
        f = ROOT.TF1(fName, LON_FIT_FORMULA, -180, 180)
        self.LonFuncDict[fName] = f
        f.SetParameter(0, 0.20)
        f.SetParameter(1, -60.)
        f.SetParameter(2, 0.02)
        f.SetLineColor(ROOT.kRed)
        numFitPars = f.GetNpar()
        if index is None:
            expr = '%s:Mean_PtLon' % varName
            gName = self.getLonGraphName(varName)
        else:
            expr = '%s[%d]:Mean_PtLon' % (varName, index)
            gName = self.getLonGraphName(varName, index)
        self.RootTree.Draw(expr, '')
        g = self.GraphCanvas.GetPrimitive('Graph')
        try:
            g.SetName(gName)
            g.SetMarkerStyle(26)
            g.SetMarkerSize(0.3)
            try:
                p.Delete()
            except:
                pass
            h = ROOT.TH2D('h2', 'h2', 50, -180, 180, 100, 0, 2)
            self.RootTree.Project('h2', expr, '')
            p = h.ProfileX()
            p.SetLineColor(ROOT.kBlue)
            p.SetLineWidth(2)
            p.Draw('same')
            p.Fit(fName, 'QRN')
            f.Draw('same')
            # If the amplitude of the longitude modulation is too small or the
            # Earth limb correction failed, disengage the longitude correction.
            if f.GetParameter(0) < 0.12 or limbSucceded == False:
                print 'Disengaging correction for the Longitude effect.'
                for i in range(numFitPars):
                    f.SetParameter(i, 0.0)
                    f.SetParError(i, 0.0)
            params = [f.GetParameter(i) for i in range(numFitPars)]
            errors = [f.GetParError(i) for i in range(numFitPars)]
            self.LonParamDict[gName] = params
            self.LonErrorDict[gName] = errors
            print '*** Variable %s %s' %\
                (varName, ('(index = %s)' % index)*(index is not None))
            for i in range(numFitPars):
                print 'p_%d = %.3e +- %.3e' % (i, params[i], errors[i])
            print 'Oscillation amplitude: %.3f\n' % f.GetParameter(0)
        except:
            print 'Procedure failed for %s.' % gName
            for i in range(numFitPars):
                f.SetParameter(i, 0.0)
                f.SetParError(i, 0.0)
            params = [f.GetParameter(i) for i in range(numFitPars)]
            errors = [f.GetParError(i) for i in range(numFitPars)]
            self.LonParamDict[gName] = params
            self.LonErrorDict[gName] = errors
            print '*** Variable %s %s' %\
                (varName, ('(index = %s)' % index)*(index is not None))
            for i in range(numFitPars):
                print 'p_%d = %.3e +- %.3e' % (i, params[i], errors[i])
            print 'Oscillation amplitude: %.3f\n' % f.GetParameter(0)
        self.GraphCanvas.Update()
        if interactive:
            raw_input('Press enter to continue.')

    def process(self, interactive = True):
        print 'Post-processing file...'
        self.GraphCanvas = ROOT.TCanvas('Graph canvas')
        self.GraphCanvas.SetGridx(True)
        self.GraphCanvas.SetGridy(True)
        cut = NOT_ROCK_ANGLE_CUT
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
        longitude = self.InputArrayDict['Mean_PtLon'][0]
        for (name, (length, type)) in VARIABLE_DICT.items():
            if name not in VARIABLE_LIST:
                self.OutputArrayDict[name][0] = self.InputArrayDict[name][0]
            elif length == 1:
                f = self.LimbFuncDict[self.getLimbFuncName(name)]
                norm = f.Eval(rockAngle)
                if norm == 0:
                    norm = 1
                f = self.LonFuncDict[self.getLonFuncName(name)]
                norm *= f.Eval(longitude)
                self.OutputArrayDict[name][0] =\
                    self.InputArrayDict[name][0]/norm
            else:
                for i in range(length):
                    f = self.LimbFuncDict[self.getLimbFuncName(name, i)]
                    norm = f.Eval(rockAngle)
                    if norm == 0:
                        norm = 1
                    f = self.LonFuncDict[self.getLonFuncName(name, i)]
                    norm *= f.Eval(longitude)
                    self.OutputArrayDict[name][i] =\
                        self.InputArrayDict[name][i]/norm



if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] rootFilePath')
    parser.add_option('-i', '--interactive', dest = 'i',
                      default = False, action = 'store_true',
                      help = 'run interactively')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    rootFilePath = args[0]
    if not rootFilePath.endswith('_proc.root'):
        parser.print_help()
        parser.error('Please give a processed input root file.')
    p = pMeritTrendPostProcessor(rootFilePath)
    p.process(interactive = opts.i)
    outputRootFilePath = rootFilePath.replace('_proc.root', '_postproc.root')
    outputFolder = os.path.dirname(rootFilePath)
    outputTextFilePath = os.path.join(outputFolder,
                                      'FactorsToNormRates_EarthLimb.txt')
    p.writeRootFile(outputRootFilePath)
    p.writeConfigFile(outputTextFilePath)
