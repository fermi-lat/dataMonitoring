import os
import sys
import logging
import commands

logging.basicConfig(level = logging.DEBUG)


BASE_REPORT_URL = 'http://glast-ground.slac.stanford.edu/Reports/'


class pDownloadManager:

    def __init__(self, downloadFolder = 'download'):
        self.DownloadFolder = downloadFolder

    def downloadUrl(self, url, options = ''):
        command = 'wget -p -nv --save-cookies cookies.txt --convert-links -nH -nd -P%s "%s%s"' %\
                  (self.DownloadFolder, url, options)
        logging.info('Executing "%s"' % command)
        logging.debug(commands.getoutput(command))

    def downloadPanel(self, name, startTime, endTime, imageFormat = 'png',
                      invalidate = False):
        url = '%sreport.jsp?reportId=%s' % (BASE_REPORT_URL, name)
        options = '&timeInterval=%d-%d&maxBins=-1&imageFormat=%s' %\
                  (startTime, endTime, imageFormat)
        if invalidate:
            options += '&invalidateWhenDone=true'
        self.downloadUrl(url, options)

    def downloadBaseReportUrl(self):
        self.downloadUrl(BASE_REPORT_URL, self.DownloadFolder)

    def cleanup(self):
        logging.info('Cleaning up download folder...')
        os.system('rm -rf %s' % self.DownloadFolder) 


if __name__ == '__main__':
    startTime = 1208649599000 - 3600*1000*24
    endTime  = 1208649599000
    downloadManager = pDownloadManager()
    downloadManager.downloadBaseReportUrl()
    downloadManager.downloadPanel('EnvPanel1', startTime, endTime)
