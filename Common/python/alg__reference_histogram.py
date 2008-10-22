
import pUtils
import math

from pSafeROOT           import ROOT
from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm

from pGlobals            import MINUS_INFINITY


## @brief Comparison against a reference histogram.
#
#  It's a variant of the chisquare test in which the comparison is made
#  bin per bin, after the histogram under study has been scaled (in terms
#  of the number of entries) to the reference histogram---we are assuming here
#  that the reference histogram does not have less entries that the object
#  the alarm is set on (so that the scaling factor is typically greater
#  than 1).
#
#  More precisely the scaling factor f is given, in terms of the total number
#  of entries in the histograms, by:
#  @f[
#  f = \frac{N_{\rm ref}}{N_{\rm test}}
#  @f]
#  The, for a fixed bin, the number of entries for the reference histogram:
#  @f[
#  n_{\rm ref} \pm \Delta n_{\rm ref}
#  @f]
#  is compared with the scaled number of entries in the corresponding bin of
#  the histogram under test:
#  @f[
#  f \cdot n_{\rm test} \pm f \cdot \Delta n_{\rm test}
#  @f]
#  and the significance s of the difference is given by:
#  @f[ 
#  s = \frac{\left| n_{\rm ref} - f \cdot n_{\rm test} \right|}
#  {\sqrt{ (\Delta n_{\rm ref})^2 +  (f \cdot \Delta n_{\rm test})^2 }}
#  @f]
#  In both cases the bin error is retrieved through the ROOT
#  TH1::GetBinError(binNumber) function so that each time the bin error is
#  properly set at creation time, the algorithm should in principle work.
#
#  <b>Output value</b>:
#
#  The significance of the <em>worst</em> bin (the one with the most
#  significance difference).
#
#  <b>Output details</b>:
#
#  @li <tt>num_warning_entries</tt>: the number of bins for which the
#  statistical significance of the difference produces a warning.
#  <br>
#  @li <tt>num_error_entries</tt>: the number of bins for which the statistical
#  significance of the difference produces an error.
#  <br>
#  @li <tt>warning_entries</tt>: a list of all the bins producing a warning.
#  Each element of the list is a string which should be self-explaining.
#  <br>
#  @li <tt>error_entries</tt>: a list of all the bins producing a warning. Each
#  element of the list is a string which should be self-explaining.
#  <br>
#  @li <tt>chisquare</tt>: the chisquare of the fit to the residuals with 
#  a constant (null) function.
#  <br>
#  @li <tt>reduced_chisquare</tt>: the reduced chisquare of the fit to the
#  residuals with a constant (null) function. 
#  <br>
# 
## @todo Update documentations.



class alg__reference_histogram(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F', 'TH1D']
    SUPPORTED_PARAMETERS = ['reference_path', 'reference_name']
    OUTPUT_LABEL         = 'Significance of the maximum bin difference'

    def __init__(self, limits, object, paramsDict, conditionsDict = {}):
        pAlarmBaseAlgorithm.__init__(self, limits, object, paramsDict,\
                                         conditionsDict)
        referenceFilePath = self.ParamsDict['reference_path']
        referenceName = self.ParamsDict['reference_name']
        self.ReferenceFile = ROOT.TFile(referenceFilePath)
        self.ReferenceObject = self.ReferenceFile.Get(referenceName)

    def run(self):
        numBins = self.ReferenceObject.GetNbinsX()
        if self.RootObject.GetNbinsX() != numBins:
            logging.error('Mismatch in bins while comparing histograms.')
            return
        numEntriesRef = self.ReferenceObject.GetEntries()
        numEntriesObj = self.RootObject.GetEntries()
        scaleFactor = numEntriesObj/float(numEntriesRef)
        chiSquare = 0
        numDof = 0
        maxBadness = MINUS_INFINITY
        outputDelta = 0
        outputBin = 0
        worstDelta = 0
        worstBin = 0
        for i in range(numBins + 2):
            exp = self.ReferenceObject.GetBinContent(i)*scaleFactor
            obs = self.RootObject.GetBinContent(i)
            deltaExp = self.ReferenceObject.GetBinError(i)*scaleFactor
            deltaObs = self.RootObject.GetBinError(i)
            try:
                delta = ((exp - obs)**2.0)/(deltaObs**2 + deltaExp**2)
                numDof += 1
                chiSquare += delta
            except ZeroDivisionError:
                delta = 0
            delta = math.sqrt(delta)
            badness = self.checkStatus(i, delta, 'difference significance')
            if badness > maxBadness:
                maxBadness = badness
                outputDelta = delta
                outputBin = i
            if delta > worstDelta:
                worstDelta = delta
                worstBin = i
        try:
            reducedChiSquare = chiSquare/float(numDof)
        except ZeroDivisionError:
            reducedChiSquare = 0
        self.Output.setDictValue('chisquare',\
                                 pUtils.formatNumber(chiSquare))
        self.Output.setDictValue('red_chisquare',\
                                 pUtils.formatNumber(reducedChiSquare))
        self.Output.setDictValue('dof', pUtils.formatNumber(numDof))
        label = self.getDetailedLabel(outputBin, outputDelta, 'delta')
        self.Output.setDictValue('output_bin', label)
        label = self.getDetailedLabel(worstBin, worstDelta, 'delta')
        self.Output.setDictValue('worst_bin', label)
        self.Output.setValue(outputDelta, None, maxBadness)
        try:
            self.ReferenceFile.Close()
        except:
            pass



if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 600, 300)
    canvas.Divide(2, 1)
    limits = pAlarmLimits(-100000, 3, -100000, 6)

    referenceFilePath = './reference.root'
    referenceName = 'reference'
    referenceFile = ROOT.TFile(referenceFilePath, 'RECREATE')
    referenceHistogram = ROOT.TH1F(referenceName, referenceName, 10, -5, 5)
    referenceHistogram.FillRandom('pol0', 1000000)
    referenceHistogram.SetMinimum(0)
    referenceHistogram.Write()
    canvas.cd(1)
    referenceHistogram.DrawCopy()
    canvas.Update()
    referenceFile.Close()
    del referenceHistogram

    canvas.cd(2)
    histogram = ROOT.TH1F('h', 'h', 10, -5, 5)
    histogram.FillRandom('pol0', 10000)
    histogram.SetMinimum(0)
    histogram.Draw()
    canvas.Update()

    pardict = {'reference_path': referenceFilePath,\
               'reference_name': referenceName}
    algorithm = alg__reference_histogram(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % algorithm.ParamsDict
    print algorithm.Output
    import os
    os.system('rm -f %s' % referenceFilePath)

