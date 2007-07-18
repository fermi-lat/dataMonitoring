
import pSafeLogger
logger = pSafeLogger.getLogger('pXmlPlotRep')

import array

from pXmlElement  import pXmlElement
from pXmlList     import pXmlList
from pSafeROOT    import ROOT


class pXmlBasePlotRep(pXmlElement):

    def __init__(self, element):        
        pXmlElement.__init__(self, element)
        self.Title        = self.getTagValue('title', self.Name)
        self.Expression   = self.getTagValue('expression')
        self.Cut          = self.getTagValue('cut'   , '')
        self.XLabel       = self.getTagValue('xlabel', '')
        self.YLabel       = self.getTagValue('ylabel', '')
        self.XLog         = self.evalTagValue('xlog', False)
        self.YLog         = self.evalTagValue('ylog', False)
        self.ZLog         = self.evalTagValue('zlog', False)
        self.DrawOptions  = self.getTagValue('drawoptions', '')
        self.Caption      = self.getTagValue('caption', '')
        if self.Cut != '':
            self.Caption += '(applied cut: "%s")' % self.Cut
        self.RootObject   = None

    def draw(self, rootObject):
        rootObject.Draw(self.DrawOptions)

    def formatRootHistogram(self):
        self.RootObject.GetXaxis().SetTitle(self.XLabel)
        self.RootObject.GetYaxis().SetTitle(self.YLabel)

    def getBranchType(self, rootTree, branchName):
        return rootTree.GetBranch(branchName).GetTitle()[-1].lower()

    def projectTree(self, rootTree, numEntries):
        if numEntries < 0:
            numEntries = 1000000000
        rootTree.Project(self.Name, self.Expression, self.Cut, '', numEntries)


class pXmlTH1FRep(pXmlBasePlotRep):

    def __init__(self, element):
        pXmlBasePlotRep.__init__(self, element)
        self.NumXBins = self.evalTagValue('xbins', 100)
        self.XMin     = self.evalTagValue('xmin')
        self.XMax     = self.evalTagValue('xmax')

    def createRootObject(self, rootTree, numEntries):
        logger.debug('Creating TH1F %s' % self.Name)
        self.RootObject = ROOT.TH1F(self.Name, self.Title, self.NumXBins,\
                                    self.XMin, self.XMax)
        self.formatRootHistogram()
        self.projectTree(rootTree, numEntries)


class pXmlTGraphRep(pXmlBasePlotRep):

    def __init__(self, element):
        pXmlBasePlotRep.__init__(self, element)

    def createRootObject(self, rootTree, numEntries):
        logger.debug('Creating TGraph %s' % self.Name)
        (xBranchName, yBranchName) = self.Expression.split(':')
        xBranchType = self.getBranchType(rootTree, xBranchName)
        yBranchType = self.getBranchType(rootTree, yBranchName)
        xArray = array.array(xBranchType, [0])
        yArray = array.array(yBranchType, [0])
        rootTree.SetBranchAddress(xBranchName, xArray)
        rootTree.SetBranchAddress(yBranchName, yArray)
        if numEntries < 0:
            numEntries = rootTree.GetEntriesFast()
        self.RootObject = ROOT.TGraph(numEntries)
        self.RootObject.SetNameTitle(self.Name, self.Title)
        for i in range(numEntries):
            rootTree.GetEntry(i)
            self.RootObject.SetPoint(i, xArray[0], yArray[0])
        ROOT.gDirectory.Add(self.RootObject)


class pXmlTH2FRep(pXmlTH1FRep):

    def __init__(self, element):
        pXmlTH1FRep.__init__(self, element)
        self.NumYBins = self.evalTagValue('ybins', 100)
        self.YMin     = self.evalTagValue('ymin')
        self.YMax     = self.evalTagValue('ymax')
        self.ZLog     = self.evalTagValue('zlog', False)

    def createRootObject(self, rootTree, numEntries):
        logger.debug('Creating TH2F %s' % self.Name)
        self.RootObject = ROOT.TH2F(self.Name, self.Title, self.NumXBins,\
                                    self.XMin, self.XMax, self.NumYBins,\
                                    self.YMin, self.YMax)
        self.formatRootHistogram()
        self.projectTree(rootTree, numEntries)

