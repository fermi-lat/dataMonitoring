
import sys
sys.path.append('../../Common/python')

from pCalBaseAnalyzer import *

HYPER_GAUSSIAN.SetParameter(0, 1000)
HYPER_GAUSSIAN.SetParameter(1, 0.)
HYPER_GAUSSIAN.SetParameter(2, 1.)
HYPER_GAUSSIAN.SetParameter(3, 2.)


def findRMSCorrectionFactors():
    histogram = ROOT.TH1F('testHisto', 'testHisto', 100, -5, 5)
    outputDict = {}
    for i in range(2, 16):
        histogram.Reset()
        HYPER_GAUSSIAN.SetParameter(3, i)
        HYPER_GAUSSIAN.FixParameter(3, i)
        histogram.FillRandom('hyper_gaussian', 1000000)
        histogram.Fit(HYPER_GAUSSIAN, 'Q')
        histogram.Draw()
        ROOT.gPad.Update()
        histogramRms = histogram.GetRMS()
        fitRms = HYPER_GAUSSIAN.GetParameter(2)
        correctionFactor = histogramRms/fitRms
        print i, histogramRms, fitRms, correctionFactor
        outputDict[i] = correctionFactor
        raw_input('Press enter to exit.')
    print outputDict

def testRMSCorrectionFactors():
    histogram = ROOT.TH1F('testHisto', 'testHisto', 100, -5, 5)
    for i in range(2, 16):
        histogram.Reset()
        HYPER_GAUSSIAN.SetParameter(3, i)
        HYPER_GAUSSIAN.FixParameter(3, i)
        histogram.FillRandom('hyper_gaussian', 1000000)
        histogram.Fit(HYPER_GAUSSIAN, 'Q')
        histogram.Draw()
        ROOT.gPad.Update()
        histogramRms = histogram.GetRMS()
        fitRms = HYPER_GAUSSIAN.GetParameter(2)*HYPER_GAUSSIAN_RMS_DICT[i]
        print i, histogramRms, fitRms
        raw_input('Press enter to exit.')


if __name__ == '__main__':
    #findRMSCorrectionFactors()
    testRMSCorrectionFactors()
