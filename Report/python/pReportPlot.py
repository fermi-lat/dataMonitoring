import os
import sys
import logging


class pReportPlot:

    def __init__(self, plotName, imageName):
        self.PlotName = plotName
        self.ImageName = imageName
        self.LeftCaption = ''
        self.RightCaption = ''

    def getLaTeXCaption(self):
        pass

    def getTextSummary(self):
        summary = 'Plot summary\n'
        summary += 'Image name   : "%s"\n' % self.ImageName
        summary += 'Right caption: "%s"\n' % self.RightCaption
        summary += 'Left caption : "%s"\n' % self.LeftCaption
        return summary

    def __str__(self):
        return self.getTextSummary()
