#!/bin/env python

from pSafeROOT import ROOT
from pM7Parser import pM7Parser

glat = ROOT.TGraph()
glon = ROOT.TGraph()
galt = ROOT.TGraph()

gjda = ROOT.TGraph()
ggms = ROOT.TGraph()
grol = ROOT.TGraph()

gra = ROOT.TGraph()
gdec= ROOT.TGraph()

gxra = ROOT.TGraph()
gxdec= ROOT.TGraph()

m7FilePath = '/home/bregeon/glast/isoc/r0236084237_080625007_v000_magic7.txt'
p = pM7Parser(m7FilePath)
p.parseIt()

print p.TimePoints[0]
i=0
for met in p.TimePoints:
    sc = p.getSCPosition((met,0))
    sc.processCoordinates()
    glat.SetPoint(i, met, sc.getLatitude())
    glon.SetPoint(i, met, sc.getLongitude())
    galt.SetPoint(i, met, sc.getAltitude())
    gjda.SetPoint(i, met, sc.JulianDate)
    ggms.SetPoint(i, met, sc.GMSTime)
    grol.SetPoint(i, met, sc.getRoll())
    gra.SetPoint(i, met, sc.getZRa())
    gdec.SetPoint(i, met, sc.getZDec())
    gxra.SetPoint(i, met, sc.getXRa())
    gxdec.SetPoint(i, met, sc.getXDec())
    i+=1

c = ROOT.TCanvas('Nav','Nav',30,50,1050,850)
c.Divide(2,2)
c.cd(1)
glat.Draw('AP*')
c.cd(2)
glon.Draw('AP*')
c.cd(3)
galt.Draw('AP*')
c.cd(4)
grol.Draw('AP*')
#gjda.Draw('AP*')

c2 = ROOT.TCanvas('Nav2','Nav2',30,50,1050,850)
c2.Divide(2,2)
c2.cd(1)
gxra.Draw('AP*')
c2.cd(2)
gxdec.Draw('AP*')
c2.cd(3)
gra.Draw('AP*')
c2.cd(4)
gdec.Draw('AP*')

c3 = ROOT.TCanvas('Nav3','Nav3',30,50,1050,850)
c3.Divide(2,2)
c3.cd(1)
ggms.Draw('AP*')
c3.cd(2)
gjda.Draw('AP*')
c3.cd(3)
gra.Draw('AP*')
c3.cd(4)
gdec.Draw('AP*')

glat.GetYaxis().SetTitle('Latitude')
glon.GetYaxis().SetTitle('Longitude')
galt.GetYaxis().SetTitle('Altitude')
gjda.GetYaxis().SetTitle('JulianDate')
ggms.GetYaxis().SetTitle('GMSTime')
grol.GetYaxis().SetTitle('RollAngle')
gra.GetYaxis().SetTitle('ZRa')
gdec.GetYaxis().SetTitle('ZDec')
gxra.GetYaxis().SetTitle('XRa')
gxdec.GetYaxis().SetTitle('XDec')


c.Update()
c2.Update()
c3.Update()
#raw_input('Exit')
