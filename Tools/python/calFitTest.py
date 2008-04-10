
import sys
sys.path.append('../../Common/python')

from pBaseAnalyzer import *


kFunction = HYPER_GAUSSIAN

kFunction.SetParameter(0, 1)
kFunction.SetParameter(1, 0.)
kFunction.SetParameter(2, 1)
kFunction.SetParameter(3, 2.)

kExponentsList = [1.1, 1.2, 1.5, 1.75, 2, 3, 4, 5, 7, 10, 15, 20]


def testHyperGaussian():
    kFunction.SetRange(-5.0, 5.0)
    for exponent in [1.1, 1.5, 2.0, 3.0]:
        kFunction.SetParameter(3, exponent)
        kFunction.Draw()
        ROOT.gPad.Update()
        raw_input('Press enter to exit.')

def findRMSCorrectionFactors():
    histogram = ROOT.TH1F('testHisto', 'testHisto', 100, -5, 5)
    fitFunction = ROOT.TF1('fit', '[0] + [1]*(x**[2])')
    graph = ROOT.TGraph()
    for (i, exponent) in enumerate(kExponentsList):
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
        graph.SetPoint(i, exponent, correctionFactor)
    ROOT.gPad.Clear()
    graph.Draw('A*')
    graph.Fit(fitFunction)
    ROOT.gPad.Update()
    constant = fitFunction.GetParameter(0)
    prefactor = fitFunction.GetParameter(1)
    index = fitFunction.GetParameter(2)
    formula = '%f + %f*(exponent**(%f))' % (constant, prefactor, index)
    print formula
    raw_input()

def testRMSCorrectionFactors():
    analyzer = pBaseAnalyzer(None, None, None)
    analyzer.FitFunction = kFunction
    histogram = ROOT.TH1F('testHisto', 'testHisto', 100, -5, 5)
    for exponent in kExponentsList:
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
    fitFunction = ROOT.TF1('fit', '[0] + [1]*(x**[2])')
    graph = ROOT.TGraph()
    for (i, exponent) in enumerate(kExponentsList):
        kFunction.SetParameter(3, exponent)
        integral = kFunction.Integral(-5, 5)
        print exponent, 1./integral
        graph.SetPoint(i, exponent, integral)
    graph.Draw('A*')
    graph.Fit(fitFunction)
    ROOT.gPad.Update()
    constant = fitFunction.GetParameter(0)
    prefactor = fitFunction.GetParameter(1)
    index = fitFunction.GetParameter(2)
    formula = '%f + %f*(exponent**(%f))' % (constant, prefactor, index)
    print formula
    raw_input()

def testNormalization():
    analyzer = pBaseAnalyzer(None, None, None)
    analyzer.FitFunction = kFunction
    for exponent in kExponentsList:
        for sigma in [0.5, 1.0, 1.5]:
            kFunction.SetParameter(3, exponent)
            kFunction.SetParameter(2, sigma)
            integral =\
                 kFunction.Integral(-5, 5)*analyzer.getNormCorrectionFactor()
            print exponent, sigma, integral



if __name__ == '__main__':
    #testHyperGaussian()
    #findRMSCorrectionFactors()
    #testRMSCorrectionFactors()
    #findNormalization()
    testNormalization()
