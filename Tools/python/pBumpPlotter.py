#!/usr/bin/env python

import os
import sys
import ROOT

ROOT.gStyle.SetCanvasColor(10)
ROOT.gStyle.SetPalette(1)


class pBumpPlotter:

    def __init__(self, inputFilePath):
        self.RootFile = ROOT.TFile(inputFilePath)
        print 'Populating run list...'
        self.RunList = []
        self.EdgeDict = {}
        for object in self.RootFile.GetListOfKeys():
            runId = object.GetName().split('_')[0]
            if runId not in self.RunList:
                self.RunList.append(runId)
        print 'Done. %s run(s) found.' % len(self.RunList)
        logFilePath = inputFilePath.replace('.root', '.log')
        if os.path.exists(logFilePath):
            self.parseLogFile(logFilePath)
        else:
            print 'Could not find log file.'
        self.Canvas = ROOT.TCanvas('bumpHunting', 'bumpHunting', 1100, 500)
        self.Canvas.Divide(4, 2)

    def parseLogFile(self, logFilePath):
        print 'Parsing log file path...'
        iterator = file(logFilePath)
        for line in iterator:
            if 'Analyzing run ' in line:
                runId = line.strip('Analyzing run ').strip('...\n')
                iterator.next()
                edges = iterator.next().strip('Peak edges: ').strip('\n')
                edges = edges.split('--')
                edges = tuple([float(edge) for edge in edges])
                self.EdgeDict[runId] = edges
        print 'Done.'

    def plot(self, outputFilePath, interactive = False):
        for runId in self.RunList:
            self.Canvas.cd(1)
            self.RootFile.Get('%s_mcIlwainL' % runId).Draw()
            self.Canvas.cd(2)
            self.RootFile.Get('%s_rate' % runId).Draw()
            if self.EdgeDict.has_key(runId):
                lines = []
                edges = self.EdgeDict[runId]
                for edge in edges:
                    ymin = self.RootFile.Get('%s_rate' % runId).GetMinimum()
                    ymax = self.RootFile.Get('%s_rate' % runId).GetMaximum()
                    line = ROOT.TLine(edge, ymin, edge, ymax)
                    line.SetLineStyle(2)
                    line.Draw('same')
                    lines.append(line)
            self.Canvas.cd(3)
            self.RootFile.Get('%s_normalized_rate' % runId).Draw()
            self.Canvas.cd(4)
            self.RootFile.Get('%s_ptpos' % runId).Draw()
            self.Canvas.cd(5)
            self.RootFile.Get('%s_map_before' % runId).Draw('colz')
            self.Canvas.cd(6)
            self.RootFile.Get('%s_map_bump' % runId).Draw('colz')
            self.Canvas.cd(7)
            self.RootFile.Get('%s_map_after' % runId).Draw('colz')
            self.Canvas.cd(8)
            self.RootFile.Get('%s_map_around' % runId).Draw('colz')
            self.Canvas.Update()
            self.Canvas.SaveAs(outputFilePath.replace('.png',\
                                                      '_%s.png' % runId))
            if interactive:
                raw_input()

    


if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser(usage = 'usage: %prog [options] rootFilePath')
    parser.add_option('-o', '--output-file', dest = 'o',
                      default = None, type = str,
                      help = 'path to the output file.')
    (opts, args) = parser.parse_args()
    if len(args) != 1:
        parser.print_help()
        parser.error('Exactly one argument required.')
    inputPath = args[0]
    plotter = pBumpPlotter(inputPath)
    plotter.plot('test.png', True)
