import os
import sys
import logging


PDFLATX_BIN = '/opt/TWWfsw/bin/pdflatex'
if not os.path.exists(PDFLATX_BIN):
    logging.info('Could not find %s, falling back to the default.' %\
                 PDFLATX_BIN)
    PDFLATX_BIN = 'pdflatex'
    

class pLaTeXWriter:

    def __init__(self, filePath = None):
        if filePath is not None:
            self.open(filePath)

    def open(self, filePath):
        self.LaTeXFilePath = filePath
        self.LaTexFolderPath = os.path.dirname(self.LaTeXFilePath)
        if self.LaTexFolderPath == '':
            sys.exit('Please do not choose the current folder for the report.')
        self.cleanup()
        try:
            self.LaTeXFile = file(self.LaTeXFilePath, 'w')
        except IOError:
            sys.exit('Could not open %s in write mode. Abort' %\
                     self.LaTeXFilePath)

    def cleanup(self):
        if not os.path.exists(self.LaTexFolderPath):
            logging.info('Creating folder %s...' % self.LaTexFolderPath)
            os.makedirs(self.LaTexFolderPath)
        else:
            logging.info('Cleaning up %s...' % self.LaTexFolderPath)
            os.system('rm -f %s/*' % self.LaTexFolderPath)

    def close(self):
        self.LaTeXFile.close()

    def write(self, text, endline = True, percent = False):
        if percent:
            text += '%'
        self.LaTeXFile.writelines(text)
        if endline:
            self.newline()

    def newline(self):
        self.LaTeXFile.writelines('\n')

    def writeHeader(self, pagesize = 'letterpaper',
                    packages = ['graphicx', 'rotating', 'color'],
                    textwidth = '19.0 truecm', textheight = '23.0 truecm',
                    margin = '-1.0 truecm'):
        self.write('\\documentclass[oneside, 12pt, %s]{report}' % pagesize)
        self.newline()
        for package in packages:
            self.write('\\usepackage{%s}' % package)
        self.newline()
        self.write('\\textwidth = %s' % textwidth)
        self.write('\\textheight = %s' % textheight)
        self.write('\\oddsidemargin %s' % margin)
        self.newline()
        self.write('\\begin{document}')
        self.newline()
        self.write('\\pagestyle{empty}')
        self.newline()
        self.startCentering()

    def writeColorText(self, text, color):
        self.write('\\textcolor{%s}{%s}' % (color, text))

    def writeTrailer(self):
        self.stopCentering()
        self.write('\\end{document}')
        self.newline()
        self.close()

    def startCentering(self):
        self.newline()
        self.write('\\begin{center}\n')
        self.newline()

    def stopCentering(self):
        self.newline()
        self.write('\\end{center}\n')
        self.newline()

    def addLogo(self, imageName = 'glastLogo.png', width = '4 cm'):
        self.write('\\begin{figure}[tbp!]')
        self.write('\\includegraphics[width=%s]{%s}' % (width, imageName))
        self.write('\\end{figure}')
        self.newline()
        
    def addPanel(self, panel, boxWidth = 0.95, plotWidth = 0.92,\
                 plotHeight = '3 cm', topMargin = '0.5 cm'):
        titleMinipageWidth = '%.2f\\linewidth' % (1 - boxWidth)
        plotMinipageWidth = '%.2f\\linewidth' % boxWidth
        labelsWidth = '%.2f\\linewidth' % ((1 - plotWidth)/2.0)
        plotWidth = '%.2f\\linewidth' % plotWidth
        self.newline()
        self.write('\\begin{figure}[htp!]')
        self.write('\\begin{minipage}[c]{%s}' % titleMinipageWidth)
        self.write('\\begin{sideways}%s\\end{sideways}' % panel.Title)
        self.write('\\end{minipage}')
        self.write('\\framebox{')
        self.write('\\begin{minipage}[c]{%s}' %  plotMinipageWidth)
        self.write('\\rule{0 cm}{%s}\\\\' % topMargin)
        for plot in panel.PlotsList:
            self.write('\\makebox[%s]{\\begin{sideways}' % labelsWidth,\
                       percent = True)
            self.write('\\makebox[%s]{\\scriptsize %s}' %\
                       (plotHeight, plot.getLeftLaTeXCaption()),\
                       percent = True)
            self.write('\\end{sideways}}', percent = True)
            self.write('\\includegraphics[width=%s]{%s}' %\
                       (plotWidth, plot.ImageName), percent = True)
            self.write('\\makebox[%s]{\\begin{sideways}' % labelsWidth,\
                       percent = True)
            self.write('\\makebox[%s]{\\scriptsize %s}' %\
                       (plotHeight, plot.getRightLaTeXCaption()),\
                       percent = True)
            self.write('\\end{sideways}}\\\\', percent = True)            
        self.write('\\end{minipage}')
        self.write('}')
        self.write('\\end{figure}')
        self.newline()

    def compile(self):
        logging.info('Compiling the report...')
        command = 'cd %s; %s %s' % (self.LaTexFolderPath, PDFLATX_BIN,
                                    os.path.basename(self.LaTeXFilePath))
        os.system(command)
 

if __name__ == '__main__':
    writer = pLaTeXWriter('./test/test.tex')
    writer.writeHeader()
    writer.writeColorText('This is a test.', 'red')
    writer.writeTrailer()
    writer.compile()
