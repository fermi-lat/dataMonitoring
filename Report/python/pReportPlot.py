import os
import sys
import logging
import re


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
    #
    #  Here is a good example for a caption:
    #  LAT Mode: <font color="black">FM</font>, <font color="red">TT</font>

    ## @var RightCaption
    ## @brief The caption to be put on the right of the plot.
    #
    #  Note that this is the html caption, as it appears on the web interface,
    #  so it needs some manipulation to be put in the LaTeX report.

    ## @var Width
    ## @brief The plot image width (in pixels).

    ## @var Height
    ## @brief The plot image height (in pixels).

    ## @var Url
    ## @brief The url the plot is linked to.

    def __init__(self, plotName, imageName):
        self.PlotName = plotName
        self.ImageName = imageName
        self.LeftCaption = ''
        self.RightCaption = ''
        self.Width = 1000.0
        self.Height = 15.0
        self.Url = 'http://glast-ground.slac.stanford.edu/Reports/'

    def getLaTeXCaption(self, caption):
        if not caption.count('</font>'):
            return caption
        latexCaption = ''
        captionPieces = caption.split('</font>')
        for piece in captionPieces:
            if piece != '':
                tag = re.search('<font.*?>', piece).group()
                color = re.search('(?<=color=").*(?=">)', piece).group()
                if re.search('_',piece): 
                    piece = piece.replace('_','\\_')
                if re.search('#',color):
                    color = self.getLaTeXColor(color)
                    latexCaption += piece.replace(tag, '\\textcolor[rgb]{%s}{' % color)
                else:
                    latexCaption += piece.replace(tag, '\\textcolor{%s}{' % color)
                latexCaption += '}'
        return latexCaption
 
    def getLeftLaTeXCaption(self):
        return self.getLaTeXCaption(self.LeftCaption)
    
    def getRightLaTeXCaption(self):
        return self.getLaTeXCaption(self.RightCaption)
    
    def getLaTeXColor(self,color):
        color = color.strip('#')
        cList = list(color) 
        r = (16*int(cList[0],16)+int(cList[1],16))/255.
        g = (16*int(cList[2],16)+int(cList[3],16))/255.
        b = (16*int(cList[4],16)+int(cList[5],16))/255.
        laTeX = '%s,%s,%s' % (r,g,b)
        return laTeX

    
    def getTextSummary(self):
        summary = 'Plot summary\n'
        summary += 'Plot Name    : "%s"\n' % self.PlotName
        summary += 'Image name   : "%s"\n' % self.ImageName
        summary += 'Right caption: "%s"\n' % self.RightCaption
        summary += 'Left caption : "%s"\n' % self.LeftCaption
        summary += 'Width        : %s\n'   % self.Width
        summary += 'Height       : %s\n'   % self.Height
        summary += 'Url          : %s'     % self.Url
        return summary

    def __str__(self):
        return self.getTextSummary()


if __name__ == '__main__':
    plot = pReportPlot('Plot-0', 'Plot-0EnvPanel1')
    plot.LeftCaption = 'Test caption'
    plot.RightCaption ='LAT Mode: <font color="black">FM</font>, <font color="red">TT</font>'
    print plot
    print plot.getLeftLaTeXCaption()
    print plot.getRightLaTeXCaption()
    
