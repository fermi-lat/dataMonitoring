
import logging
logging.basicConfig(level = logging.DEBUG)

import sys
import ROOT
import numpy
import math

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetCanvasColor(10)
ROOT.gStyle.SetOptStat(0)

from __polygons__ import *

ROOT_TREE_NAME = 'LrsTree'


class lrsPlotter:

    def __init__(self, rootFilePath, counterName):
        self.RootFile = ROOT.TFile(rootFilePath)
        self.RootTree = self.RootFile.Get(ROOT_TREE_NAME)
        self.CounterName = counterName
        self.createArrays()
        self.createHistograms()
        self.OriginalPolygon = polygon(ORIGINAL_POLYGON)
        self.NewPolygon = polygon(ROB_POLYGON)
        self.loop()

    def createArrays(self):
        logging.info('Creating arrays...')
        self.Time = numpy.zeros((1), 'd')
        self.Longitude = numpy.zeros((1), 'd')
        self.Latitude = numpy.zeros((1), 'd')
        self.Rate = numpy.zeros((1), 'd')
        self.SAAFlag = numpy.zeros((1), 'd')
        self.RootTree.SetBranchAddress('Time', self.Time)
        self.RootTree.SetBranchAddress('LSPGEOLON', self.Longitude)
        self.RootTree.SetBranchAddress('LSPGEOLAT', self.Latitude)
        self.RootTree.SetBranchAddress(self.CounterName, self.Rate)
        self.RootTree.SetBranchAddress('SACFLAGLATINSAA', self.SAAFlag)

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
        numEntries = self.RootTree.GetEntries()
        totalTime = 0
        timeInSaaOriginal = 0
        timeInSaaNew = 0
        timeInBetween = 0
        self.RootTree.GetEntry(0)
        previousTime = self.Time[0]
        logging.info('Starting event loop...')
        for i in xrange(numEntries):
            if (i%100000) == 0:
                logging.debug('%d events scanned.' % i)
            self.RootTree.GetEntry(i)
            (x, y) = (self.Longitude, self.Latitude)
            dt = self.Time[0] - previousTime
            if dt < 0:
                print 'Error: dt = %f' % dt
            else:
                totalTime += dt
                if self.SAAFlag > 0:
                    timeInSaaOriginal += dt
                    if self.NewPolygon.isInside(x, y):
                        timeInSaaNew += dt
                    else:
                        timeInBetween += dt
            self.RateHistogram.Fill(x, y, self.Rate)
            self.ExposureHistogram.Fill(x, y, 1)
            previousTime = self.Time[0]
        self.RateHistogram.Divide(self.ExposureHistogram)
        print 'Total time: %f s' % totalTime
        print 'Time in original SAA: %f s (%f)' % (timeInSaaOriginal,
                                                   timeInSaaOriginal/totalTime)
        print 'Time in new SAA: %f s (%f)' % (timeInSaaNew,
                                              timeInSaaNew/totalTime)
        print 'Time in new between: %f s (%f)' % (timeInBetween,
                                                  timeInBetween/totalTime)

    def draw(self):
        self.Canvas = ROOT.TCanvas('canvas_%s' % self.CounterName,
                                   self.CounterName, 800, 500)
        self.Canvas.SetLogz(True)
        self.RateHistogram.Draw('colz')
        self.OriginalPolygon.draw(True)
        self.NewPolygon.draw(True, 2, ROOT.kRed)
        self.Canvas.Update()


if __name__ == '__main__':
    #calHiplotter = lrsPlotter('/data/work/leo/saa/calLrsChain.root',\
    #                              'LrsHiAverageRate')
    #calHiplotter.draw()
    #calLoplotter = lrsPlotter('/data/work/leo/saa/calLrsChain.root',\
    #                              'LrsLoAverageRate')
    #calLoplotter.draw()
    tkrPlotter = lrsPlotter('/data/work/leo/saa/tkrLrsChain.root',\
                                'LrsAverageRate')
    tkrPlotter.draw()
    #acdPlotter = lrsPlotter('/data/work/leo/saa/acdLrsChain.root',\
    #                            'LrsAverageRate')
    #acdPlotter.draw()
    

