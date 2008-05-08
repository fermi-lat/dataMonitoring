import os
import sys
import logging


class pReportPlot:

    ## @var PlotName
    ## @brief The name of the plot, as it appears in the html on the web
    #  interface (i.e. Plot-0).

    ## @var ImageName
    ## @brief The image name, as it is saved right after the wget, not
    #  including the extension (i.e. Plot-0EnvPanel1)

    ## @var LeftCaption
    ## @brief The caption to be put on the left of the plot.
    #
    #  Note that this is the html caption, as it appears on the web interface,
    #  so it needs some manipulation to be put in the LaTeX report.

    ## @var RightCaption
    ## @brief The caption to be put on the right of the plot.
    #
    #  Note that this is the html caption, as it appears on the web interface,
    #  so it needs some manipulation to be put in the LaTeX report.

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
