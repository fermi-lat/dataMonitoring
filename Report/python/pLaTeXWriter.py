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

    def writeHeader(self):
        self.write('\\input{../preamble}')
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

    def addPageHeader(self, timeSpan, logoName = 'glastLogo',\
                      logoWidth = '2cm'):
        self.write('\\begin{figure}[htp!]')
        self.write('\\includegraphics[width=%s]{glastLogo}' % logoWidth,\
                   percent = True)
        self.write('\\hfill %s \hfill' % timeSpan)
        self.write('\\includegraphics[width=%s]{glastLogo}' % logoWidth,\
                   percent = True)
        self.write('\\end{figure}')
        self.newline()

    def addPage(self, page, timeSpan):
        logging.info('Adding new page...')
        self.addPageHeader(timeSpan)
        for panel in page.PanelsList:
            self.addPanel(panel)
        self.write('\\clearpage')
        self.newline()
        
    def addPanel(self, panel, boxWidth = 0.95, plotWidth = 0.92,\
                 topMargin = '0.5 cm'):
        labelLineWidth = '%.2f\\linewidth' % ((1 - plotWidth)/2.0)
        plotLineWidth = '%.2f\\linewidth' % plotWidth
        self.newline()
        self.write('\\begin{figure}[htp!]')
        self.write('\\gpanellabel{%.2f\\linewidth}{%s}' %\
                   ((1 - boxWidth), panel.Title))
        self.write('\\gpanelplot{%.2f\\linewidth}{%s}{\\\\' %\
                   (boxWidth, topMargin))
        for plot in panel.PlotsList:
            plotLineHeight = '%.2f\\linewidth' %\
                             (plotWidth*(plot.Height/plot.Width))
            self.write('\\gplotlabel{%s}{%s}{%s}' %\
                       (labelLineWidth, plotLineHeight,\
                        plot.getLeftLaTeXCaption()),  percent = True)
            self.write('\\includegraphics[width=%s]{%s}' %\
                       (plotLineWidth, plot.ImageName), percent = True)
            self.write('\\gplotlabel{%s}{%s}{%s}\\\\' %\
                       (labelLineWidth, plotLineHeight,\
                        plot.getRightLaTeXCaption()))
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
