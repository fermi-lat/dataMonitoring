import ROOT

ROOT.gStyle.SetOptStat(111111)
ROOT.gStyle.SetMarkerStyle(26)
ROOT.gStyle.SetMarkerSize(0.3)
ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetCanvasColor(10)
ROOT.gStyle.SetFrameBorderMode(0)
ROOT.gStyle.SetFrameFillColor(0)
ROOT.gStyle.SetPadBorderMode(0)
ROOT.gStyle.SetPadColor(0)
ROOT.gStyle.SetHistFillStyle(0)
ROOT.gStyle.SetStatColor(10)
ROOT.gStyle.SetGridColor(16)
ROOT.gStyle.SetLegendBorderSize(1)
ROOT.gStyle.SetTitleYOffset(1.1)
ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(111111)
ROOT.gStyle.SetPaintTextFormat("1.2g")
ROOT.gStyle.SetTitleSize(0.06, 'XY')
ROOT.gStyle.SetTitleOffset(1.00, 'X')
ROOT.gStyle.SetTitleOffset(0.60, 'Y')

# Miscellanea dimensions
TEXT_STYLE   = 43
TEXT_SIZE    = 22
TITLE_SIZE   = 25
LABEL_SIZE   = 20
LINE_WIDTH   = 2
TICK_LENGTH_Y = 0.015

# Style settings.
TITLE_OFFSET_X = 1.0
TITLE_OFFSET_Y = 0.6

TITLE_OFFSET_X_DOUBLE = 3.0
TITLE_OFFSET_Y_DOUBLE = 1.2

ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetTextFont(TEXT_STYLE)
ROOT.gStyle.SetTextSize(TEXT_SIZE)
ROOT.gStyle.SetLabelFont(TEXT_STYLE, 'XY')
ROOT.gStyle.SetLabelSize(LABEL_SIZE, 'XY')
ROOT.gStyle.SetTitleFont(TEXT_STYLE, 'XY')
ROOT.gStyle.SetTitleSize(TITLE_SIZE, 'XY')
ROOT.gStyle.SetTitleOffset(TITLE_OFFSET_X, 'X')
ROOT.gStyle.SetTitleOffset(TITLE_OFFSET_Y, 'Y')
ROOT.gStyle.SetNdivisions(510, 'X')
ROOT.gStyle.SetNdivisions(505, 'Y')
ROOT.gStyle.SetTickLength(0.03, 'X')
ROOT.gStyle.SetTickLength(TICK_LENGTH_Y, 'Y')
ROOT.gStyle.SetPadTickX(True)
ROOT.gStyle.SetPadTickY(True)


OBJECT_POOL = []

def store(rootObject):
    OBJECT_POOL.append(rootObject)

def getCanvas(name, title = None, width = 800, height = 500, grid = False):
    title = title or name
    canvas = ROOT.TCanvas(name, title, width, height)
    canvas.SetBottomMargin(1.25*(TITLE_SIZE + LABEL_SIZE)/height)
    canvas.SetRightMargin(0.9*(TEXT_SIZE)/width)
    canvas.SetTopMargin(1.3*(TEXT_SIZE)/height)
    canvas.SetLeftMargin(1.8*(TITLE_SIZE + LABEL_SIZE)/width)
    if grid:
        canvas.SetGridx(True)
        canvas.SetGridy(True)
    store(canvas)
    return canvas

def getSkinnyCanvas(name, title = None, grid = False):
    return getCanvas(name, title, 1000, 400, grid)
