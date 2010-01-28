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


MIN_TIME = utc2met(convert2sec('Jan/19/2010 00:00:00'))
MAX_TIME = utc2met(convert2sec('Jan/22/2010 00:00:00'))
BIG_TILE_EXP = 'OutF_Normalized_AcdHit_AcdTile[63]'
ALL_TILES_EXP = BIG_TILE_EXP
for i in range(48, 63):
    ALL_TILES_EXP += ' + OutF_Normalized_AcdHit_AcdTile[%d]' % i
NORMALIZE = True


gFile = ROOT.TFile(os.path.join(TARGET_DIR, 'goes.root'))
gTree = gFile.Get('Time')
gTree.Draw('FluxLong:Timestamp', 'FluxLong > 0')
gGOES = ROOT.gPad.GetPrimitive('Graph').Clone()
gGOES.SetLineColor(ROOT.kRed)
gGOES.GetXaxis().SetTitle('Time UTC')
gGOES.GetXaxis().SetNdivisions(506)
gGOES.GetXaxis().SetLabelSize(LABEL_SIZE)
gGOES.GetXaxis().SetTimeDisplay(True)
gGOES.GetXaxis().SetTimeFormat(TIME_FORMAT)
gGOES.GetXaxis().SetRangeUser(MIN_TIME, MAX_TIME)
gGOES.GetYaxis().SetTitle('GOES-14 x-ray Flux 1.0-8.0 A (Wm^{-2})')
gGOES.GetYaxis().SetLabelSize(LABEL_SIZE)
gGOES.GetYaxis().SetRangeUser(1e-9, 1e-4)

dFile = ROOT.TFile(os.path.join(TARGET_DIR, 'goes_digi.root'))
dTree = dFile.Get('Time')
dTree.AddFriend('Time', os.path.join(TARGET_DIR, 'goes_merit.root'))
dTree.Draw('%s:TimeStampFirstEvt' % BIG_TILE_EXP)
gFermi = ROOT.gPad.GetPrimitive('Graph').Clone()
if NORMALIZE:
    fnorm = ROOT.TF1('fnorm', 'pol1')
    dTree.Draw('%s:Mean_PtMcIlwainL' % BIG_TILE_EXP)
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
gFermi.GetXaxis().SetTitle('Time UTC')
gFermi.GetXaxis().SetNdivisions(506)
gFermi.GetXaxis().SetLabelSize(LABEL_SIZE)
gFermi.GetXaxis().SetTimeDisplay(True)
gFermi.GetXaxis().SetTimeFormat(TIME_FORMAT)
gFermi.GetXaxis().SetRangeUser(MIN_TIME, MAX_TIME)
gFermi.GetYaxis().SetTitle('Acd hit tiles')
gFermi.GetYaxis().SetLabelSize(LABEL_SIZE)

canvas = ROOT.TCanvas('c', 'c', 1100, 700)
canvas.Divide(1, 2)
canvas.cd(1)
ROOT.gPad.SetLogy(True)
ROOT.gPad.SetGridx(True)
ROOT.gPad.SetGridy(True)
gGOES.Draw('al')
canvas.cd(2)
ROOT.gPad.SetGridx(True)
ROOT.gPad.SetGridy(True)
gFermi.Draw('al')
canvas.Update()
