from pSafeROOT import ROOT

from pAlarmBaseAlgorithm import pAlarmBaseAlgorithm


## @brief Normalization of a gaussian fit.
#
#  <b>Valid parameters</b>:
#
#  @li <tt>min</tt>: the minimum x value for the fit range.
#  <br>
#  @li <tt>max</tt>: the maximum x value for the fit range.
#
#  <b>Output value</b>:
#
#  The mean value of the gaussian fit in the user-defined sub-range.


class alg__gauss_norm(pAlarmBaseAlgorithm):

    SUPPORTED_TYPES      = ['TH1F']
    SUPPORTED_PARAMETERS = ['min', 'max']
    OUTPUT_LABEL         = 'Normalization of the gaussian fit'

    def run(self):
        gaussian = ROOT.TF1('alg__gaussian', 'gaus')
        self.Output.setValue(self.getFitParameter(gaussian, 0))


if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(30, 50, 10, 70)
    canvas = ROOT.TCanvas('Test canvas', 'Test canvas', 400, 400)

    print
    print 'Testing on a 1-dimensional histogram...'
    histogram = ROOT.TH1F('h', 'h', 100, -5, 5)
    function = ROOT.TF1('f', 'gaus')
    function.SetParameter(0, 1)
    function.SetParameter(1, 2)
    function.SetParameter(2, 1)
    histogram.FillRandom('f', 1000)
    function.SetParameter(1, -2)
    histogram.FillRandom('f', 1000)
    histogram.Draw()
    canvas.Update()
    pardict = {'min': 0, 'max': 4}
    algorithm = alg__gauss_norm(limits, histogram, pardict)
    algorithm.apply()
    print 'Parameters: %s\n' % pardict
    print algorithm.Output

