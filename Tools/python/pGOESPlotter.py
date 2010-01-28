import os
import sys
import math

sys.path.append('../../Common/python')
sys.path.append('../../Report/python')

from pTimeUtils import *
from pSafeROOT  import ROOT
from pGOESDownloader import *
from pLongTermTrendPlotter import *
from pTimeUtils import *

ROOT.gStyle.SetTitleSize(0.05, 'X')
ROOT.gStyle.SetTitleSize(0.05, 'Y')
ROOT.gStyle.SetLabelSize(0.05, 'X')
ROOT.gStyle.SetLabelSize(0.05, 'Y')

#MIN_TIME = utc2met(convert2sec('Jan/19/2010 07:00:00'))
#MAX_TIME = utc2met(convert2sec('Jan/21/2010 03:00:00'))

#MIN_TIME = utc2met(convert2sec('Jan/19/2010 13:00:00'))
#MAX_TIME = utc2met(convert2sec('Jan/19/2010 21:00:00'))

MIN_TIME = utc2met(convert2sec('Jan/20/2010 10:00:00'))
MAX_TIME = utc2met(convert2sec('Jan/20/2010 19:00:00'))

BIG_TILE_EXP  = 'OutF_Normalized_AcdHit_AcdTile[63]'
ALL_TILES_EXP = 'OutF_Normalized_AcdHit_AcdTile[63]'
for i in range(48, 63):
    ALL_TILES_EXP += ' + OutF_Normalized_AcdHit_AcdTile[%d]' % i
NORMALIZE = False
TIME_EXP  = '(0.5*(Bin_End + Bin_Start))'
VALUE_EXP = BIG_TILE_EXP
MIN_GOES  = 1e-9 
MAX_GOES  = 1e-4
if NORMALIZE:
    MIN_LAT   = 0.5
    MAX_LAT   = 4
else:
    MIN_LAT   = 0.1
    MAX_LAT   = 0.75
TIME_FORMAT = '%b %d 20%y %H:%M%F2001-01-01 00:00:00'

FLARE_DICT = {'A': 8,
              'B': 7,
              'C': 6,
              'M': 5,
              'X': 4
              }


gFile = ROOT.TFile(os.path.join(TARGET_DIR, 'goes.root'))
gTree = gFile.Get('Time')
gTree.Draw('FluxLong:Timestamp', 'FluxLong > 0')
gGOES = ROOT.gPad.GetPrimitive('Graph').Clone()
gGOES.SetLineColor(ROOT.kRed)
gGOES.SetLineWidth(2)
gGOES.GetXaxis().SetTitle('Time UTC')
gGOES.GetXaxis().SetNdivisions(506)
gGOES.GetXaxis().SetLabelSize(LABEL_SIZE)
gGOES.GetXaxis().SetTimeDisplay(True)
gGOES.GetXaxis().SetTimeFormat(TIME_FORMAT)
gGOES.GetXaxis().SetRangeUser(MIN_TIME, MAX_TIME)
gGOES.GetXaxis().SetLabelSize(0.05)
gGOES.GetYaxis().SetTitle('#splitline{GOES-14 x-ray Flux 1.0-8.0 A (Wm^{-2})}{reference for the flare classification}')
gGOES.GetYaxis().SetLabelSize(LABEL_SIZE)
gGOES.GetYaxis().SetRangeUser(MIN_GOES, MAX_GOES)
gGOES.GetYaxis().SetLabelSize(0.05)

dFile = ROOT.TFile(os.path.join(TARGET_DIR, 'goes_digi.root'))
dTree = dFile.Get('Time')
dTree.AddFriend('Time', os.path.join(TARGET_DIR, 'goes_merit.root'))
dTree.Draw('%s:%s' % (VALUE_EXP, TIME_EXP))
gFermi = ROOT.gPad.GetPrimitive('Graph').Clone()
if NORMALIZE:
    fnorm = ROOT.TF1('fnorm', 'pol1')
    dTree.Draw('%s:Mean_PtMcIlwainL' % VALUE_EXP)
    g = ROOT.gPad.GetPrimitive('Graph')
    g.Fit('fnorm')
    x = ROOT.Double()
    y = ROOT.Double()
    for i in xrange(dTree.GetEntries()):
        dTree.GetEntry(i)
        norm = fnorm.Eval(dTree.Mean_PtMcIlwainL)
        gFermi.GetPoint(i, x, y)
        gFermi.SetPoint(i, x, y/norm)
gFermi.SetLineColor(ROOT.kBlue)
gFermi.SetLineWidth(2)
gFermi.GetXaxis().SetTitle('Time UTC')
gFermi.GetXaxis().SetNdivisions(506)
gFermi.GetXaxis().SetLabelSize(LABEL_SIZE)
gFermi.GetXaxis().SetTimeDisplay(True)
gFermi.GetXaxis().SetTimeFormat(TIME_FORMAT)
gFermi.GetXaxis().SetRangeUser(MIN_TIME, MAX_TIME)
gFermi.GetXaxis().SetLabelSize(0.05)
gFermi.GetYaxis().SetTitle('#splitline{ACD tile 63 (side +X) occupancy}{over the hit (not veto) threshold}')
gFermi.GetYaxis().SetLabelSize(LABEL_SIZE)
gFermi.GetYaxis().SetRangeUser(MIN_LAT, MAX_LAT)
gFermi.GetYaxis().SetLabelSize(0.05)

canvas = ROOT.TCanvas('c', 'c', 900, 700)
canvas.Divide(1, 2)
canvas.cd(1)
ROOT.gPad.SetLogy(True)
ROOT.gPad.SetGridx(True)
ROOT.gPad.SetGridy(True)
ROOT.gPad.SetRightMargin(0.03)
ROOT.gPad.SetLeftMargin(0.1)
gGOES.Draw('al')
labelList = []
for (text, exp) in FLARE_DICT.items():
    label = ROOT.TLatex(MAX_TIME, 2.5*(10**-exp), '  %s' % text)
    label.Draw()
    labelList.append(label)
canvas.cd(2)
ROOT.gPad.SetGridx(True)
ROOT.gPad.SetGridy(True)
ROOT.gPad.SetRightMargin(0.03)
ROOT.gPad.SetLeftMargin(0.1)
gFermi.Draw('al')
canvas.Update()

# Parse the file with the flag in the SAA.
insun = False
t1 = None
t2 = None
boxList = []
for line in file(os.path.join(TARGET_DIR, 'goes_sunflag.csv')):
    if line.startswith('"'):
        date, timestamp, flag = line.strip('\n').split(',')
        timestamp = float(timestamp)
        timestamp = utc2met(timestamp)
        if timestamp > MIN_TIME and timestamp < MAX_TIME:
            flag = float(flag) > 0.5
            if not flag and insun is True:
                print 'Exiting light at met %f' % timestamp
                insun = False
                t1 = timestamp
            elif flag and insun is False:
                print 'Entering light at met %f' % timestamp
                insun = True
                t2 = timestamp
                if t1 is not None:
                    canvas.cd(1)
                    box = ROOT.TBox(t1, MIN_GOES, t2, MAX_GOES)
                    box.SetFillStyle(3003)
                    box.SetFillColor(ROOT.kBlack)
                    box.Draw()
                    boxList.append(box)
                    canvas.cd(2)
                    box = ROOT.TBox(t1, MIN_LAT, t2, MAX_LAT)
                    box.SetFillStyle(3003)
                    box.SetFillColor(ROOT.kBlack)
                    box.Draw()
                    boxList.append(box)

ROOT.gPad.Update()

# Parse the file with the flag in the SAA.
insaa = False
t1 = None
t2 = None
for line in file(os.path.join(TARGET_DIR, 'goes_saaflag.csv')):
    if line.startswith('"'):
        date, timestamp, flag = line.strip('\n').split(',')
        timestamp = float(timestamp)
        timestamp = utc2met(timestamp)
        if timestamp > MIN_TIME and timestamp < MAX_TIME:
            flag = float(flag) > 0.5
            if not flag and insaa is True:
                print 'Exiting saa at met %f' % timestamp
                insaa = False
                t2 = timestamp
                if t1 is not None:
                    canvas.cd(1)
                    box = ROOT.TBox(t1, MIN_GOES, t2, MAX_GOES)
                    box.SetFillStyle(1001)
                    box.SetFillColor(ROOT.kGray)
                    box.Draw()
                    boxList.append(box)
                    canvas.cd(2)
                    box = ROOT.TBox(t1, MIN_LAT, t2, MAX_LAT)
                    box.SetFillStyle(1001)
                    box.SetFillColor(ROOT.kGray)
                    box.Draw()
                    boxList.append(box)
            elif flag and insaa is False:
                print 'Entering saa at met %f' % timestamp
                insaa = True
                t1 = timestamp

canvas.cd(1)
gGOES.Draw('l,same')
ROOT.gPad.Update()
