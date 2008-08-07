import os
import sys
import logging


#PDFLATX_BIN = '/opt/TWWfsw/bin/pdflatex'
#if not os.path.exists(PDFLATX_BIN):
#    logging.debug('Could not find %s, falling back to the default.' %\
#                 PDFLATX_BIN)
#    PDFLATX_BIN = 'pdflatex'
PDFLATX_BIN = 'pdflatex -interaction="nonstopmode"'
    

class pLaTeXWriter:

    def __init__(self, filePath = None):
        if filePath is not None:
            self.open(filePath)

    def open(self, filePath):
        self.LaTeXFilePath = filePath
        self.LaTeXFolderPath = os.path.dirname(self.LaTeXFilePath)
        if self.LaTeXFolderPath == '':
            sys.exit('Please do not choose the current folder for the report.')
        self.__cleanup()
        try:
            self.LaTeXFile = file(self.LaTeXFilePath, 'w')
        except IOError:
            sys.exit('Could not open %s in write mode. Abort' %\
                     self.LaTeXFilePath)

    def __cleanup(self):
        if not os.path.exists(self.LaTeXFolderPath):
            logging.info('Creating folder %s...' % self.LaTeXFolderPath)
            os.makedirs(self.LaTeXFolderPath)
        else:
            logging.info('Cleaning up %s...' % self.LaTeXFolderPath)
            os.system('rm -f %s/*' % self.LaTeXFolderPath)

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
        self.write('\\input{./preamble}')
        self.newline()
        self.write('\\begin{document}')
        self.newline()
        self.write('\\pagestyle{empty}')
        self.newline()
        #self.startCentering()

    def writeColorText(self, text, color):
        self.write('\\textcolor{%s}{%s}' % (color, text))

    def writeTrailer(self):
        #self.stopCentering()
        self.write('\\end{document}')
        self.newline()
        self.close()

    def startCentering(self):
        self.write('\\begin{center}\n')
        self.newline()

    def stopCentering(self):
        self.write('\\end{center}\n')
        self.newline()

    def addLogo(self, imageName = 'glastLogo.png', width = '4 cm'):
        self.write('\\begin{figure}[tbp!]')
        self.write('\\includegraphics[width=%s]{%s}' % (width, imageName))
        self.write('\\end{figure}')
        self.newline()

    def addPageHeader(self, title, timeSpan, logoName = 'glastLogo',\
                      logoWidth = '2.3cm'):
        self.write('\\begin{figure}[htp!]')
        self.write('\\parbox[c]{0.99\\textwidth}{', percent=True)
        self.write('\\parbox[c]{0.12\\textwidth}{', percent=True)
        self.write('\\includegraphics[width=%s]{glastLogo}}' % logoWidth,\
                       percent = True)
        self.write('\\hfill\\parbox{0.7\\textwidth}{\\begin{center}',\
                       percent = True)
        self.write('%s\\\\%s' % (title, timeSpan), percent=True)
        self.write('\\end{center}}\\hfill', percent = True)
        self.write('\\parbox[c]{0.12\\textwidth}{', percent=True)
        self.write('\\includegraphics[width=%s]{glastLogo}}' % logoWidth,\
                       percent = True)
        self.write('}')
        self.write('\\end{figure}')
        self.newline()

    def addPage(self, page, title, timeSpan):
        logging.info('Adding new page...')
        self.startCentering()
        self.addPageHeader(title, timeSpan)
        for panel in page.PanelsList:
            self.addPanel(panel)
        self.stopCentering()
        self.write('\\clearpage')
        self.newline()

    def addTelemetryPage(self, page, title, timeSpan):
        logging.info('Adding new page...')
        self.startCentering()
        self.addPageHeader(title, timeSpan)
        for panel in page.PanelsList:
            self.addTelemetryPanel(panel)
        self.stopCentering()
        self.write('\\clearpage')
        self.newline()
        
    def addPanel(self, panel, boxWidth = 0.93, plotWidth = 0.91,\
                 topMargin = '0.0 cm'):
        labelLineWidth = '%.2f\\linewidth' % ((1 - plotWidth)/2.0)
        plotLineWidth = '%.2f\\linewidth' % plotWidth
        self.write('\\vspace*{-10pt}')
        self.write('\\begin{figure}[htp!]')
        self.write('\\gpanellabel{0.03\\linewidth}{%s}' % panel.Title)
        self.write('\\gpanelplot{%.2f\\linewidth}{%s}{\\\\' %\
                   (boxWidth, topMargin))
        for plot in panel.PlotsList:
            plotLineHeight = '%.3f\\linewidth' %\
                             (plotWidth*(plot.Height/plot.Width)/2)
            self.write('\\vspace*{-15pt}\\\\')
            self.write('\\gplotleftlabel{%s}{%s}' %\
                       (plotLineHeight,\
                        plot.getLeftLaTeXCaption()),  percent = True)
            #self.write('\href{%s}{\\includegraphics[width=%s]{%s}}' %\
            #           (plot.Url,plotLineWidth, plot.ImageName), percent=True)
            self.write('\\includegraphics[width=%s]{%s}' %\
                       (plotLineWidth, plot.ImageName), percent=True)
            self.write('\\gplotrightlabel{%s}{%s}\\\\' %\
                       (plotLineHeight,\
                        plot.getRightLaTeXCaption()))
        self.write('\\vspace*{-12pt}')
        self.write('}')
        self.write('\\end{figure}')
        self.newline()
        self.write('\\vspace*{-10pt}')

    def addTelemetryPanel(self, panel, boxWidth = 1.00, plotWidth = 0.86,\
                 topMargin = '0.0 cm'):
        labelLineWidth = '%.2f\\linewidth' % ((1 - plotWidth)/2.0)
        plotLineWidth = '%.2f\\linewidth' % plotWidth
        self.write('\hspace*{-15pt}')
        self.write('\\vspace*{-10pt}')
        self.write('\\begin{figure}[htp!]')
        self.write('\\gpanelplot{%.2f\\linewidth}{%s}{\\\\' %\
                   (boxWidth, topMargin))
        for plot in panel.PlotsList:
            plotLineHeight = '%.3f\\linewidth' %\
                             (plotWidth*(plot.Height/plot.Width)/2)
            self.write('\\vspace*{-15pt}\\\\')
            self.write('\\gplotleftlabel{%s}{%s}' %\
                       (plotLineHeight,\
                        plot.getLeftLaTeXCaption()),  percent = True)
            #self.write('\href{%s}{\\includegraphics[width=%s]{%s}}' %\
            #           (plot.Url,plotLineWidth, plot.ImageName), percent=True)
            self.write('\\includegraphics[width=%s]{%s}' %\
                       (plotLineWidth, plot.ImageName), percent=True)
            self.write('\\gplotrightlabel{%s}{%s}\\\\' %\
                       (plotLineHeight,\
                        plot.getRightLaTeXCaption()))
        self.write('\\vspace*{-12pt}')
        self.write('}')
        self.write('\\end{figure}')
        self.newline()
        self.write('\\vspace*{-10pt}')

    def compile(self):
        logging.info('Compiling the report...')
        command = 'cd %s; %s %s' % (self.LaTeXFolderPath, PDFLATX_BIN,
                                    os.path.basename(self.LaTeXFilePath))
        os.system(command)
 

if __name__ == '__main__':
    writer = pLaTeXWriter('./test/test.tex')
    writer.writeHeader()
    writer.writeColorText('This is a test.', 'red')
    writer.writeTrailer()
    writer.compile()
