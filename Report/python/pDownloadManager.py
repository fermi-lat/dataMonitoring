import os
import sys
import logging
import commands

logging.basicConfig(level = logging.DEBUG)


BASE_REPORT_URL  = 'http://glast-ground.slac.stanford.edu/Reports/'
INVALIDATE_URL   = '%s%s' % (BASE_REPORT_URL, 'invalidateSession')
COOKIE_FILE_PATH = 'cookies.txt'


class pDownloadManager:

    def __init__(self, downloadFolder):
        self.DownloadFolder = downloadFolder

    def downloadUrl(self, url, options = '', saveCookies = False):
        command  = 'wget -p -nv --convert-links -nH -nd '
        if saveCookies:
            logging.debug('Storing cookies in %s...' % COOKIE_FILE_PATH)
            command += '--save-cookies %s ' % COOKIE_FILE_PATH
        else:
            logging.debug('Loading cookies from %s...' % COOKIE_FILE_PATH)
            command += '--load-cookies %s ' % COOKIE_FILE_PATH
        command += '--keep-session-cookies -P%s "%s%s"' %\
                   (self.DownloadFolder, url, options)
        logging.info('Executing "%s"' % command)
        logging.info(commands.getoutput(command))

    def downloadPanel(self, name, startTime, endTime, imageFormat = 'png'):
        url = '%sreport.jsp?reportId=%s' % (BASE_REPORT_URL, name)
        options = '&timeInterval=%d-%d&maxBins=-1&imageFormat=%s' %\
                  (startTime, endTime, imageFormat)
        self.downloadUrl(url, options, False)

    def downloadBaseReportUrl(self):
        self.downloadUrl(BASE_REPORT_URL, '', True)

    def invalidateSession(self):
        logging.debug('Invalidating session...')
        self.downloadUrl(INVALIDATE_URL)
        self.cleanup()
        self.cleanupCookies()

    def cleanup(self):
        logging.info('Cleaning up download folder...')
        os.system('rm -rf %s' % self.DownloadFolder)

    def cleanupCookies(self):
        logging.info('Removing stored cookies...')
        os.system('rm -f %s' % COOKIE_FILE_PATH)


if __name__ == '__main__':
    startTime = 1208649599000 - 3600*1000*24
    endTime  = 1208649599000
    downloadManager = pDownloadManager('download')
    downloadManager.downloadBaseReportUrl()
    downloadManager.downloadPanel('EnvPanel1', startTime, endTime)
