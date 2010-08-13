
from pMeritTrendPostProcessor import *


BRANCH_LIST = ['EvtsBeforeCuts',
               'DiffuseEvts',
               'SourceEvts']

TIME_EXP = '0.5*(Bin_Start + Bin_End)'
THRESHOLD = 2.5


class pMeritTrendTester(pMeritTrendPostProcessor):

    def __init__(self, meritTrendFilePath, normRootFilePath):
        self.MeritTrendFile = ROOT.TFile(meritTrendFilePath)
        self.MeritTrendTree = self.MeritTrendFile.Get('Time')
        self.NormRootFile = ROOT.TFile(normRootFilePath)
        self.NumEntries = self.MeritTrendTree.GetEntries()
        self.OrigCanvas = None
        self.NewCanvas = None

    def draw(self, branchName):
        # Draw the normalized rate from the original merit trend file.
        print 'Reading the original normalized values...'
        origNormBranchName = 'OutF_NormRate%s' % branchName
        self.OrigGraph = ROOT.TGraphErrors()
        self.OrigGraph.SetMarkerStyle(23)
        for i in xrange(self.NumEntries):
            self.MeritTrendTree.GetEntry(i)
            t = 0.5*(self.MeritTrendTree.Bin_Start +\
                         self.MeritTrendTree.Bin_End)
            value = eval('self.MeritTrendTree.%s' % origNormBranchName)
            error = eval('self.MeritTrendTree.%s_err' % origNormBranchName)
            if value > THRESHOLD:
                rockAngle = self.MeritTrendTree.Mean_PtSCzenith
                mcIlwainL = self.MeritTrendTree.Mean_PtMcIlwainL
                print '%s value = %.3f +- %.3f (L = %.3f, rock angle = %.3f)' %\
                    (origNormBranchName, value, error, mcIlwainL, rockAngle)
            self.OrigGraph.SetPoint(i, t, value)
            self.OrigGraph.SetPointError(i, 0, error)
        if self.OrigCanvas is None:
            self.OrigCanvas = ROOT.TCanvas('cOrig', 'Original normalized rate')
            self.OrigCanvas.SetGridy(True)
        else:
            self.OrigCanvas.cd()
            self.OrigCanvas.Clear()
        self.OrigGraph.Draw('ap')
        self.OrigCanvas.Update()
        print 'Done.'
        # And now the new normalized rate.
        print 'Calculating the new normalization factors...'
        unnormBranchName = 'Rate_%s' % branchName
        hRate = self.NormRootFile.Get('h%s' % unnormBranchName)
        fLimb = self.NormRootFile.Get('fLimb_gLimb%s' % unnormBranchName)
        fLon = self.NormRootFile.Get('fLon_gLon%s' % unnormBranchName)
        self.NewGraph = ROOT.TGraphErrors()
        self.NewGraph.SetMarkerStyle(23)
        for i in xrange(self.NumEntries):
            self.MeritTrendTree.GetEntry(i)
            t = 0.5*(self.MeritTrendTree.Bin_Start +\
                         self.MeritTrendTree.Bin_End)
            # Retrieve the un-normalized rate
            value = eval('self.MeritTrendTree.%s' % unnormBranchName)
            error = eval('self.MeritTrendTree.%s_err' % unnormBranchName)
            # Correct for McIlwainL
            mcIlwainL = self.MeritTrendTree.Mean_PtMcIlwainL
            bin = int(200*(mcIlwainL - MIN_L)/(MAX_L - MIN_L)) + 1
            norm = hRate.GetBinContent(bin)
            value /= norm
            error /= norm
            # Correct for rocking angle
            rockAngle = self.MeritTrendTree.Mean_PtSCzenith
            norm = fLimb.Eval(rockAngle)
            value /= norm
            error /= norm
            # Correct for the longitude modulation
            longitude = self.MeritTrendTree.Mean_PtLon
            norm = fLon.Eval(longitude)
            value /= norm
            error /= norm
            if value > THRESHOLD:
                print '%s value = %.3f +- %.3f(L = %.3f, rock angle = %.3f)' %\
                    (origNormBranchName, value, error, mcIlwainL, rockAngle)
            self.NewGraph.SetPoint(i, t, value)
            self.NewGraph.SetPointError(i, 0, error)
        if self.NewCanvas is None:
            self.NewCanvas = ROOT.TCanvas('cNew', 'New normalized rate')
            self.NewCanvas.SetGridy(True)
        else:
            self.NewCanvas.cd()
            self.NewCanvas.Clear()
        self.NewGraph.Draw('ap')
        self.NewCanvas.Update()
        print 'Done.'




if __name__ == '__main__':
    t = pMeritTrendTester(
        '/data/work/datamon/runs/normrates/r0303054436_merittrend.root',
        #'/data/work/datamon/runs/normrates/r0302951541_merittrend.root',
        #'/data/work/datamon/runs/normrates/r0303123354_merittrend.root',
        'normrates_v2/merit_norm_postproc.root')
    for branchName in BRANCH_LIST:
        t.draw(branchName)
        raw_input('Press enter to continue...')
