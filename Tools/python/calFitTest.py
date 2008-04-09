
import sys
sys.path.append('../../Common/python')

from pCalBaseAnalyzer import *


kFunction = HYPER_GAUSSIAN

kFunction.SetParameter(0, 1)
kFunction.SetParameter(1, 0.)
kFunction.SetParameter(2, 1)
kFunction.SetParameter(3, 2.)


def findRMSCorrectionFactors():
    histogram = ROOT.TH1F('testHisto', 'testHisto', 100, -5, 5)
    outputDict = {}
    for exponent in range(2, 16):
        histogram.Reset()
        kFunction.FixParameter(3, exponent)
        histogram.FillRandom('hyper_gaussian', 1000000)
        histogram.Fit(kFunction, 'Q')
        histogram.Draw()
        ROOT.gPad.Update()
        histogramRms = histogram.GetRMS()
        fitRms = kFunction.GetParameter(2)
        correctionFactor = histogramRms/fitRms
        print exponent, histogramRms, fitRms, correctionFactor
        outputDict[i] = correctionFactor
        raw_input('Press enter to exit.')
    print outputDict

def testRMSCorrectionFactors():
    analyzer = pCalBaseAnalyzer(None, None, None)
    analyzer.FitFunction = kFunction
    histogram = ROOT.TH1F('testHisto', 'testHisto', 100, -5, 5)
    for exponent in range(2, 16):
        histogram.Reset()
        kFunction.FixParameter(3, exponent)
        histogram.FillRandom('hyper_gaussian', 1000000)
        histogram.Fit(kFunction, 'Q')
        histogram.Draw()
        ROOT.gPad.Update()
        histogramRms = histogram.GetRMS()
        fitRms = kFunction.GetParameter(2)*analyzer.getRmsCorrectionFactor()
        print exponent, histogramRms, fitRms
        raw_input('Press enter to exit.')

def findNormalization():
    outputDict = {}
    for exponent in range(2, 16):
        kFunction.SetParameter(3, exponent)
        integral = kFunction.Integral(-5, 5)
        print exponent, integral
        outputDict[exponent] = 1./integral
    print outputDict

def testNormalization():
    analyzer = pCalBaseAnalyzer(None, None, None)
    analyzer.FitFunction = kFunction
    for exponent in range(2, 16):
        for sigma in [0.5, 1.0, 1.5]:
            kFunction.SetParameter(3, exponent)
            kFunction.SetParameter(2, sigma)
            integral =\
                 kFunction.Integral(-5, 5)*analyzer.getNormCorrectionFactor()
            print exponent, sigma, integral



if __name__ == '__main__':
    #findRMSCorrectionFactors()
    #testRMSCorrectionFactors()
    #findNormalization()
    testNormalization()
