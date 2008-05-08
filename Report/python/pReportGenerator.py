#!/bin/env python

import os
import logging
import re

logging.basicConfig(level = logging.DEBUG)

from pLaTeXWriter     import pLaTeXWriter
from pReportPanel     import pReportPanel
from pDownloadManager import pDownloadManager


LOGO_IMAGE_NAME = 'glastLogo.png'

    

class pReportGenerator(pLaTeXWriter, pDownloadManager):
    
    def __init__(self, startTime, endTime):
        pDownloadManager.__init__(self)
        self.StartTime = startTime
        self.EndTime = endTime
        self.PanelsList = []

    def writeReport(self, outputFilePath):
        pLaTeXWriter.__init__(self, outputFilePath)
        self.writeHeader()
        logging.info('Copying the GLAST logo into the report folder...')
        os.system('cp %s %s' % (LOGO_IMAGE_NAME, self.LaTexFolderPath))
        self.addLogo()
        self.processIndex()
        self.processPanels()
        self.writeTrailer()

    def processIndex(self):
        self.downloadBaseReportUrl()
        for line in file('%s/index.html' % self.DownloadFolder).readlines():
            if 'Panel' in line and 'href' in line:
                panelName = re.search('(?<=reportId=).*(?=">)', line).group()
                self.PanelsList.append(panelName)
            if 'UTC' in line:
                timeSpan = line.strip().replace('<b>', '').replace('</b>', '')
                self.write('%s\n' % timeSpan)
        pDownloadManager.cleanup(self)

    def processPanels(self):
        for panelName in self.PanelsList:
            panel = pReportPanel(panelName, self.StartTime, self.EndTime)
            self.addPanel(panel)

 

if __name__ == '__main__':
    startTime = 1208649599000 - 3600*1000*24
    endTime  = 1208649599000
    reportGenerator = pReportGenerator(startTime, endTime)
    reportGenerator.writeReport('./tex/report.tex')
    reportGenerator.compile()

