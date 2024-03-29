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

    def __init__(self, name, startTime, endTime, reportFolder,\
                     downloadFolder, cookieFolder, imageFormat = 'png'):
        pDownloadManager.__init__(self, downloadFolder, cookieFolder)
        self.Name = name
        self.Title = name
        self.ImageFormat = imageFormat
        self.ReportFolder = reportFolder
        if not os.path.exists(self.ReportFolder):
            logging.info('Creating directory %s...' % self.ReportFolder)
            os.makedirs(self.ReportFolder)
        self.PlotNamesList = []
        self.PlotsList = []
        self.downloadInfo(startTime, endTime)
        self.PageContent = self.__retrievePageContent()
        self.processInfo()
        self.cleanup()

    ## @brief Download all the panel-related stuff from the server.
        
    def downloadInfo(self, startTime, endTime):
        logging.info('Downloading panel %s...' % self.Name)
        self.downloadPanel(self.Name, startTime, endTime, self.ImageFormat)

    ## @brief Grab all the downloaded images, rename them and move them
    #  into the report directory, so that they're ready for being compiled.
    #
    #  The list of plots for the panel is also filled.

    def processImages(self):
        logging.info('Processing panel images...')
        imagesList = glob(os.path.join(self.DownloadFolder, 'aida_plot*'))
        for plotName in self.PlotNamesList:
            for string in imagesList:
                if plotName in string:
                    imageName = '%s%s' % (plotName, self.Name)
                    imagePath = '%s/%s.%s' %\
                        (self.ReportFolder, imageName, self.ImageFormat)
                    if not os.path.exists(string):
                        logging.error('Could not find %s.' % string)
                    else:
                        command = 'mv "%s" %s' % (string, imagePath)
                        logging.debug('Executing %s...' % command)
                        os.system(command)
                        self.PlotsList.append(pReportPlot(plotName, imageName))
                    break

    ## @brief Read the html panel page and return the relevant content
    #  as a single string.
    #
    #  The "relevant part" of the page is defined as everything following
    #  the panel title (identified by means of the <h2/> html tag), excluding
    #  the blank lines.

    def __retrievePageContent(self):
        try:
            titleFound = False
            pageContent = ''
            for line in file(glob('%s/report*' %\
                                      self.DownloadFolder)[0]).readlines():
                if '<h2' in line:
                    titleFound = True
                if titleFound and not line.isspace():
                    pageContent += line
                if '<img width="' in line:
                    plotName = line.split('name=')[1]
                    plotName = plotName.split('&amp')[0]
                    self.PlotNamesList.append(plotName)
            return pageContent
        except:
            logging.error('Could not parse html content for panel %s.' %\
                          self.Name)
            return None

    ## @brief Grab the content of the html panel page and extract the
    #  relevant information (i.e. panel title, plot labels etc.)
    #
    #  This is a little bit involuted, it could surely be better.

    def processPage(self):
        logging.info('Processing panel page...')
        if self.PageContent is None:
            return
        self.Title = re.search('(?<=>).*(?=</h2>)', self.PageContent).group()
        htmlTableRows = re.search('(?<=<tr).*(?=</tr>)', self.PageContent,\
                                      re.DOTALL).group().split('</tr>')
        for plot in self.PlotsList:
            plot.Url = self.PanelUrl
            for htmlTableRow in htmlTableRows:
                if plot.PlotName in htmlTableRow:
                    caption = re.search('leftCaption.*?</td>',\
                                        htmlTableRow, re.DOTALL).group()
                    caption = caption.split('\n')[2].strip()
                    caption = caption.replace('</b>', '')
                    plot.LeftCaption = caption
                    caption = re.search('rightCaption.*?</td>',\
                                        htmlTableRow, re.DOTALL).group()
                    caption = caption.split('\n')[2].strip()
                    caption = caption.replace('</b>', '')
                    plot.RightCaption = caption
                    dims = re.search('<img width=.*?height=.*?src=',\
                                     htmlTableRow, re.DOTALL).group()
                    width = re.search('(?<=width=").*?(?=")', dims).group()
                    height = re.search('(?<=height=").*?(?=")', dims).group()
                    plot.Width = float(width)
                    plot.Height = float(height)
                    href = re.search('href.*?</td>', htmlTableRow, re.DOTALL)
                    if href:
                        http = href.group() 
                        plot.Url = http.split('"')[1].strip()

            logging.debug(plot)

    def processInfo(self):
        self.processImages()
        self.processPage()



if __name__ == '__main__':
    startTime = 1208649599000 - 3600*1000*24
    endTime  = 1208649599000
    panel = pReportPanel('EnvPanel1', startTime, endTime)
    raw_input('')
    panel.cleanup()
