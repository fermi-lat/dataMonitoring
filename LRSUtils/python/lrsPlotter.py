
import logging
logging.basicConfig(level = logging.DEBUG)

import sys
import ROOT
import numpy
import math

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

SAA_LON = [-92.0, -99.5, -98.3, -95.4, -90.9, -66.1, -48.7, -37.3, -28.4,
            33.2, 42.1, 47.5]
SAA_LAT = [-30.0, -16.5, -11.1, -7.1, -4.4, 2.7, 6.5, 8.5, 8.4, -17.4,
            -22.3, -30.0]
SAA_CENTER = (-40, -20)

RATE_THRESHOLD = 1000.
TIME_BIN_WIDTH = 20.


class lrsTransition:
    
    def __init__(self, timestamp, polarity, longitude, latitude):
        self.Timestamp = timestamp
        self.Polarity = polarity
        self.Longitude = longitude
        self.Latitude = latitude
        self.DistanceFromSAACenter =\
            math.sqrt((self.Longitude - SAA_CENTER[0])**2 +\
                          (self.Latitude - SAA_CENTER[1])**2)  
        self.AngleToSAACenter = 0
        self.Marker = ROOT.TMarker(self.Longitude, self.Latitude, 8)

    def draw(self):
        self.Marker.Draw('same')

    def __cmp__(self):
        return 0

    def __str__(self):
        str = 'Transition at %f s, (%.2f, %.2f), polarity = %d\n' %\
            (self.Timestamp, self.Longitude, self.Latitude, self.Polarity)
        str += 'Distance to SAA center: %.2f' % self.DistanceFromSAACenter
        return str
        


class lrsPlotter:

    def __init__(self, rootFilePath, counterName):
        self.RootFile = ROOT.TFile(rootFilePath)
        self.RootTree = self.RootFile.Get(ROOT_TREE_NAME)
        self.CounterName = counterName
        self.createArrays()
        self.createHistograms()
        self.createSAAContour()
        self.loop()

    def createSAAContour(self):
        SAA_LAT.append(SAA_LAT[0])
        SAA_LON.append(SAA_LON[0])
        self.SAAContour = []
        for i in range(12):
            line = ROOT.TLine(SAA_LON[i], SAA_LAT[i], SAA_LON[i + 1],
                              SAA_LAT[i + 1])
            line.SetLineWidth(2)
            self.SAAContour.append(line)

    def createArrays(self):
        logging.info('Creating arrays...')
        self.Time = numpy.zeros((1), 'd')
        self.Longitude = numpy.zeros((1), 'd')
        self.Latitude = numpy.zeros((1), 'd')
        self.Rate = numpy.zeros((1), 'd')
        self.RootTree.SetBranchAddress('Time', self.Time)
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
        self.TransitionsList = []
        self.RootTree.GetEntry(0)
        startTime = self.Time[0]
        timeWindow = [startTime, startTime + TIME_BIN_WIDTH]
        averageRate = 0
        numCounts = 0
        previousAverageRate = self.Rate[0]
        previousTime = self.Time[0]
        previousLongitude = self.Longitude[0]
        previousLatitude = self.Latitude[0]
        logging.info('Starting event loop...')
        for i in range(self.RootTree.GetEntries()):
            if (i%100000) == 0:
                logging.debug('%d events scanned.' % i)
            self.RootTree.GetEntry(i)
            self.RateHistogram.Fill(self.Longitude, self.Latitude, self.Rate)
            self.ExposureHistogram.Fill(self.Longitude, self.Latitude, 1)
            averageRate += self.Rate[0]
            numCounts += 1
            if self.Time > timeWindow[1]:
                averageRate /= numCounts
                if averageRate >= RATE_THRESHOLD and\
                        previousAverageRate < RATE_THRESHOLD:
                    t = lrsTransition(previousTime, 1, previousLongitude,
                                      previousLatitude)
                    self.TransitionsList.append(t)
                elif averageRate <= RATE_THRESHOLD and\
                        previousAverageRate > RATE_THRESHOLD:
                    t = lrsTransition(previousTime, -1, previousLongitude,
                                      previousLatitude)
                    self.TransitionsList.append(t)
                t = int((self.Time[0] - startTime)/TIME_BIN_WIDTH)
                timeWindow = (t, t + TIME_BIN_WIDTH)
                previousAverageRate = averageRate
                previousTime = self.Time[0]
                previousLongitude = self.Longitude[0]
                previousLatitude = self.Latitude[0]
                averageRate = 0
                numCounts = 0
        self.RateHistogram.Divide(self.ExposureHistogram)

    def draw(self):
        self.Canvas = ROOT.TCanvas('canvas_%s' % self.CounterName,
                                   self.CounterName, 800, 500)
        self.Canvas.SetLogz(True)
        self.RateHistogram.Draw('colz')
        for line in self.SAAContour:
            line.Draw('same')
        self.Canvas.Update()
        raw_input('Press enter to draw the SAA transitions...')
        print '%d transitions found.' % len(self.TransitionsList)
        for transition in self.TransitionsList:
            print transition
            transition.draw()
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
    
    # -35, -45, 0, 5 @ 121439326...
