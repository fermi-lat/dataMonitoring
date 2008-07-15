import ROOT
import os
import sys


ORIGINAL_POLYGON = [(-92.0, -30.0),
                    (-99.5, -16.5),
                    (-98.3, -11.1),
                    (-95.4, -7.1 ),
                    (-90.9, -4.4 ),
                    (-66.1, 2.7  ),
                    (-48.7, 6.5  ),
                    (-37.3, 8.5  ),
                    (-28.4, 8.4  ),
                    (33.2 , -17.4),
                    (42.1 , -22.3),
                    (47.5 , -30.0)
                    ]
ROB_POLYGON      = [(-86.1, -30.0),
                    (-92.1, -21.7),
                    (-98.5, -12.5),
                    (-97.5, -9.9 ),
                    (-93.1, -8.6 ),
                    (-58.8, 0.7  ),
                    (-42.0, 4.6  ),
                    (-36.0, 5.2  ),
                    (-25.7, 5.2  ),
                    (-18.6, 2.5  ),
                    (24.5 , -22.6),
                    (33.9 , -30.0)
                    ]

MIN_LON = -180
MAX_LON = 180
MIN_LAT = -30
MAX_LAT = 30
NUM_LON_BINS = 300
NUM_LAT_BINS = 200


class polygon:

    def __init__(self, vertexList):
        self.VertexList = vertexList
        self.VertexList.append(self.VertexList[0])
        self.LinesList = []
        self.ConditionsList = []
        for i in range(len(vertexList) - 1):
            lon1 = self.VertexList[i][0]
            lat1 = self.VertexList[i][1]
            lon2 = self.VertexList[i+1][0]
            lat2 = self.VertexList[i+1][1]
            self.LinesList.append(ROOT.TLine(lon1, lat1, lon2, lat2))
        self.BaseHistogram = ROOT.TH2F('SAA', 'SAA', NUM_LON_BINS, MIN_LON,
                                      MAX_LON, NUM_LAT_BINS, MIN_LAT, MAX_LAT)

    def isInside(self, x0, y0):
        xIntercepts = []
        for line in self.LinesList:
            if (line.GetY1() < y0) == (line.GetY2() > y0):
                x1 = line.GetX1()
                y1 = line.GetY1()
                x2 = line.GetX2()
                y2 = line.GetY2()
                xIntercepts.append((x2 - x1)*(y0 - y1)/(y2 - y1) + x1)
        if xIntercepts == []:
            return False
        else:
            return (x0 > min(xIntercepts) and x0 < max(xIntercepts))

    def draw(self, superimpose = False, lineWidth = 2, lineColor = ROOT.kBlack):
        if not superimpose:
            self.BaseHistogram.Draw()
        for line in self.LinesList:
            line.SetLineColor(lineColor)
            line.SetLineWidth(lineWidth)
            line.Draw('same')
        ROOT.gPad.Update()


if __name__ == '__main__':
    p = polygon(ORIGINAL_POLYGON)
    p.draw()
    p2 = polygon(ROB_POLYGON)
    p2.draw(True, 2, ROOT.kRed)
    
    #import random
    #markers = []
    #for i in range(10000):
    #    x = random.uniform(MIN_LON, MAX_LON)
    #    y = random.uniform(MIN_LAT, MAX_LAT)
    #    m = ROOT.TMarker(x, y, 26)
    #    m.SetMarkerSize(0.6)
    #    if p.isInside(x, y):
    #        m.SetMarkerColor(ROOT.kRed)
    #    markers.append(m)
    #    m.Draw('same')
    ROOT.gPad.Update()
