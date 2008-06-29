
import logging
logging.basicConfig(level = logging.DEBUG)

import sys
import ROOT
import numpy

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetCanvasColor(10)
ROOT.gStyle.SetOptStat(0)

MIN_LON = -180
MAX_LON = 180
MIN_LAT = -30
MAX_LAT = 30
NUM_LON_BINS = 300
NUM_LAT_BINS = 200
ROOT_TREE_NAME = 'LrsTree'


class lrsPlotter:

    def __init__(self, rootFilePath, counterName):
        self.RootFile = ROOT.TFile(rootFilePath)
        self.RootTree = self.RootFile.Get(ROOT_TREE_NAME)
        self.CounterName = counterName
        self.createArrays()
        self.createHistograms()
        self.loop()

    def createArrays(self):
        logging.info('Creating arrays...')
        self.Longitude = numpy.zeros((1), 'd')
        self.Latitude = numpy.zeros((1), 'd')
        self.Rate = numpy.zeros((1), 'd')
        self.RootTree.SetBranchAddress('LSPGEOLON', self.Longitude)
        self.RootTree.SetBranchAddress('LSPGEOLAT', self.Latitude)
        self.RootTree.SetBranchAddress(self.CounterName, self.Rate)

    def createHistograms(self):
        logging.info('Creating histograms...')
        self.ExposureHistogram = ROOT.TH2F('exposure_%s' % self.CounterName,
                                           'LRS exposure',
                                           NUM_LON_BINS, MIN_LON, MAX_LON,
                                           NUM_LAT_BINS, MIN_LAT, MAX_LAT)
        self.ExposureHistogram.GetXaxis().SetTitle('Latitude')
        self.ExposureHistogram.GetYaxis().SetTitle('Longitude')
        self.RateHistogram = ROOT.TH2F('rate_%s' % self.CounterName,
                                       'LRS average rate (Hz)',
                                       NUM_LON_BINS, MIN_LON, MAX_LON,
                                       NUM_LAT_BINS, MIN_LAT, MAX_LAT)
        self.RateHistogram.GetXaxis().SetTitle('Latitude')
        self.RateHistogram.GetYaxis().SetTitle('Longitude')

    def loop(self):
        logging.info('Starting event loop...')
        for i in range(self.RootTree.GetEntries()):
            if (i%100000) == 0:
                logging.debug('%d events scanned.' % i)
            self.RootTree.GetEntry(i)
            self.RateHistogram.Fill(self.Longitude, self.Latitude, self.Rate)
            self.ExposureHistogram.Fill(self.Longitude, self.Latitude, 1)
        self.RateHistogram.Divide(self.ExposureHistogram)

    def draw(self):
        self.Canvas = ROOT.TCanvas('canvas_%s' % self.CounterName,
                                   self.CounterName, 800, 500)
        self.RateHistogram.Draw('colz')
        self.Canvas.SetLogz(True)
        self.Canvas.Update()


if __name__ == '__main__':
    calLoplotter = lrsPlotter('/data/work/leo/saa/calLrsChain.root',\
                                  'LrsLoAverageRate')
    calLoplotter.draw()
    tkrPlotter = lrsPlotter('/data/work/leo/saa/tkrLrsChain.root',\
                                'LrsAverageRate')
    tkrPlotter.draw()
    
