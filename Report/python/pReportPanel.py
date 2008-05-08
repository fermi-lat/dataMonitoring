import os
import sys
import re
import logging

logging.basicConfig(level = logging.DEBUG)

from glob             import glob
from pDownloadManager import pDownloadManager
from pReportPlot      import pReportPlot


class pReportPanel(pDownloadManager):

    ## @brief Basic constructor.

    def __init__(self, name, startTime, endTime, imageFormat = 'png',\
                 downloadFolder = 'download', reportFolder = 'tex'):
        self.Name = name
        self.ImageFormat = imageFormat
        self.DownloadFolder = downloadFolder
        self.ReportFolder = reportFolder
        if not os.path.exists(self.ReportFolder):
            logging.info('Creating directory %s...' % self.ReportFolder)
            os.makedirs(self.ReportFolder)
        self.PlotsList = []
        self.downloadInfo(startTime, endTime)
        self.processInfo()

    ## @brief Download all the panel-related stuff from the server.
        
    def downloadInfo(self, startTime, endTime):
        logging.info('Downloading panel %s...' % self.Name)
        self.downloadPanel(self.Name, startTime, endTime, self.ImageFormat,\
                           self.DownloadFolder)

    ## @brief Grab all the downloaded images, rename them and move them
    #  into the report directory, so that they're ready for being compiled.
    #
    #  The list of plots for the panel is also filled.

    def processImages(self):
        logging.info('Processing panel images...')
        imagesList = glob(os.path.join(self.DownloadFolder, 'aida_plot*'))
        imagesList.sort()
        for string in imagesList:
            plotName = re.search('(?<=name=).*(?=&width)', string).group()
            imageName = '%s%s' % (plotName, self.Name)
            imagePath = '%s/%s.%s' %\
                        (self.ReportFolder, imageName, self.ImageFormat)
            command = 'mv "%s" %s' % (string, imagePath)
            logging.debug('Executing %s...' % command)
            os.system(command)
            self.PlotsList.append(pReportPlot(plotName, imageName))

    ## @brief Read the html panel page and return the relevant content
    #  as a single string.
    #
    #  The "relevant part" of the page is defined as everything following
    #  the panel title (identified by means of the <h2/> html tag), excluding
    #  the blank lines.

    def getPageContent(self):
        titleFound = False
        pageContent = ''
        for line in file(glob('./download/report*')[0]).readlines():
            if '<h2' in line:
                titleFound = True
            if titleFound and not line.isspace():
                pageContent += line
        return pageContent

    ## @brief Grab the content of the html panel page and extract the
    #  relevant information (i.e. panel title, plot labels etc.)
    #
    #  This is a little bit involuted, it could surely be better.

    def processPage(self):
        logging.info('Processing panel page...')
        pageContent = self.getPageContent()
        self.Title = re.search('(?<=>).*(?=</h2>)', pageContent).group()
        print self.Title
        htmlTableRows = re.search('(?<=<tr).*(?=</tr>)', pageContent,\
                                      re.DOTALL).group().split('</tr>')
        for plot in self.PlotsList:
            for htmlTableRow in htmlTableRows:
                if plot.PlotName in htmlTableRow:
                    caption = re.search('leftCaption.*?</td>',\
                                        htmlTableRow, re.DOTALL).group()
                    caption = caption.split('\n')[1].strip()
                    caption = caption.replace('</td>', '')
                    plot.LeftCaption = caption
                    caption = re.search('rightCaption.*?</td>',\
                                        htmlTableRow, re.DOTALL).group()
                    caption = caption.split('\n')[1].strip()
                    caption = caption.replace('</td>', '')
                    plot.RightCaption = caption
            print plot

        
    def processInfo(self):
        self.processImages()
        self.processPage()

    def cleanup(self):
        logging.info('Cleaning up %s...' % self.DownloadFolder)
        os.system('rm -rf %s' % self.DownloadFolder)
        logging.info('Done.')



if __name__ == '__main__':
    startTime = 1208649599000 - 3600*1000*24
    endTime  = 1208649599000
    panel = pReportPanel('EnvPanel1', startTime, endTime)
    raw_input('')
    panel.cleanup()
