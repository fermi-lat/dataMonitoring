import os
import sys
import logging
import commands

logging.basicConfig(level = logging.DEBUG)


BASE_REPORT_URL = 'http://glast-ground.slac.stanford.edu/Reports/'
DOWNLOAD_FOLDER = 'download'


class pDownloadManager:

    def downloadUrl(self, url, targetFolder = DOWNLOAD_FOLDER,\
                    options = ''):
        command = 'wget -p -nv --convert-links -nH -nd -P%s %s %s' %\
                  (targetFolder, url, options)
        logging.info('Executing "%s"' % command)
        logging.debug(commands.getoutput(command))

    def downloadPanel(self, name, startTime, endTime, imageFormat = 'png',\
                      targetFolder = DOWNLOAD_FOLDER):
        url = '%sreport.jsp?reportId=%s' % (BASE_REPORT_URL, name)
        self.downloadUrl(url, targetFolder,\
                         '&timeInterval=%d-%d&maxBins=-1&imageFormat=%s' %\
                         (startTime, endTime, imageFormat))

    def downloadBaseReportUrl(self, targetFolder = DOWNLOAD_FOLDER):
        self.downloadUrl(BASE_REPORT_URL, targetFolder)
    


if __name__ == '__main__':
    startTime = 1208649599000 - 3600*1000*24
    endTime  = 1208649599000
    downloadManager = pDownloadManager()
    downloadManager.downloadBaseReportUrl()
    downloadManager.downloadPanel('EnvPanel1', startTime, endTime)
