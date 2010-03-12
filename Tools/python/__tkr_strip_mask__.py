
from __future__ import division   #sembra essere necessario per fare le
import os
import sys
import ROOT
import math

from pRootStyle import *
ROOT.gStyle.SetOptStat(0)

STRIP_MASK_DICT = {

      #  Tower        0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15

    '1-Pre-launch': [18,  4,  8,  7,  3, 10, 18, 15, 13,  9, 21, 15, 26,  8, 18, 10], 
    '2-OBCONF-49' : [ 0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0],
    '3-OBCONF-66' : [ 9,  0,  2,  0,  0,  0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0],
    '4-OBCONF-86' : [52,  0,  1,  0,  1,  0,  0,  0,  7,  1,  0,  0,  0,  0,  0,  0],
    '5-OBCONF-97' : [29,  0,  1,  2,  0,  1,  0,  0,  0,  1,  1,  0,  0,  0,  0,  0],
    '6-OBCONF-105': [ 3,  0,  1,  2,  1,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    '7-OBCONF-118': [ 0,  0,  0,  2,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    '8-OBCONF-120': [ 0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
    '9-OBCONF-121': [ 0,  0,  0,  0,  0,  2,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0]}   #333 Masked Strips


# --  Tower --      0  --   1  --   2  --   3  --   4  --   5  --   6  --   7  --   8  --   9  --   10 --   11 --   12 --   13 --   14 --   15  

HIT_SLOPE =      [-0.1229, -0.0046, -0.0059, -0.0038, -0.0081, -0.0161, -0.0039, -0.0024, -0.0048, -0.0061, -0.0079,  0.0006,  0.0002,  0.0042, -0.0020,  0.0001] 
ERR_HIT_SLOPE=   [ 0.0076,  0.0023,  0.0015,  0.0016,  0.0023,  0.0028,  0.0016,  0.0016,  0.0018,  0.0030,  0.0017,  0.0016,  0.0021,  0.0023,  0.0015,  0.0010]
 
AVERAGE_HIT=     [ 98.49,  99.84,  99.95,  99.94,  99.83,  99.74,  99.92,  99.94,  99.90,  99.70,  99.91,  99.94,  99.89,  99.84,  99.95,  99.96]
ERR_AVERAGE_HIT= [  0.06,   0.02,   0.01,   0.01,   0.02,   0.02,   0.01,   0.01,   0.02,   0.02,   0.01,   0.01,   0.02,   0.02,   0.01,   0.01]

NUM_TOWER_STRIP =  55296
NUM_LAT_STRIP   =  884736 

Delta_T_Correct = 0.0159                                                                   #1.59 years /100 

def getOBNumMaskedStrips(key, tower):
    return STRIP_MASK_DICT[key][tower]

def getOBTotalNumMaskedStrips(key):
    return sum(STRIP_MASK_DICT[key])

def getNumMaskedStrips(key, tower):
    KEY_LIST= STRIP_MASK_DICT.keys()
   # if key not in KEY_LIST:
   #     print 'Key "%s" not in key list. Abort.' % KEY_LIST
   #     sys.exit()
    KEY_LIST.sort()
    STRIP_TOTAL=0
    for i in KEY_LIST[1:]:
        if i != key: 
            STRIP_TOTAL=STRIP_TOTAL+ getOBNumMaskedStrips(i, tower)
        else:
            return STRIP_TOTAL+ getOBNumMaskedStrips(key, tower)
        
def getTotalNumMaskedStrips(key):                                      
    TOWER_LIST = range(16)
    STRIP_ALL_TOTAL=0
    for i in TOWER_LIST: 
        STRIP_ALL_TOTAL=STRIP_ALL_TOTAL+ getNumMaskedStrips(key, i)
       
    return STRIP_ALL_TOTAL
 
def makeCorrelPlot(effmin = -0.2e-3, effmax = 2.2e-3):
    effmin *= 100
    effmax *= 100
    h = ROOT.TH1F('h', 'h', 1000, effmin, effmax)
    h.SetMinimum(effmin)
    h.SetMaximum(effmax)
    for i in range(1002):
        h.SetBinContent(i, -1)
    h.GetXaxis().SetTitle('Fraction of strips masked (%)')
    h.GetYaxis().SetTitle('Hit efficiency loss in 1.5 years (%)')
    store(h)
    TOWER_LIST  = range(16)
    D_Eps_Mask  = []
    D_Eps_Slope = []
    g = ROOT.TGraphErrors()
    g.SetMarkerSize(0.7)
    store(g)
    
    for m in TOWER_LIST:
        D_Eps_Mask.append(getNumMaskedStrips('9-OBCONF-121',m)/NUM_TOWER_STRIP)
        D_Eps_Slope.append(-HIT_SLOPE[m]*Delta_T_Correct)
        g.SetPoint(m, 100*D_Eps_Mask[m], 100*D_Eps_Slope[m])
        g.SetPointError(m, 0, 100*ERR_HIT_SLOPE[m]*Delta_T_Correct)

    f = ROOT.TF1('bisect', 'x', effmin, effmax)
    store(f)
    f.SetLineStyle(7)
    c = getCanvas('strip')
    store(c)
    h.Draw()
    g.Draw('p')
    f.Draw('same')
    label = ROOT.TLatex(0.175, 0.19, 'Tower A')
    label.SetTextColor(ROOT.kBlue)
    store(label)
    label.Draw()
    c.Update()
    saveCanvas(c, 'mask_eff_corr.eps')

    
                
if __name__ == '__main__':
   # print getOBNumMaskedStrips('Pre-launch', 15)
   # print getOBTotalNumMaskedStrips('Pre-launch')
   # print getNumMaskedStrips('9-OBCONF-121',0)
    makeCorrelPlot()
