#!/bin/env python
import os
from glob import glob

# end of the time interval and duration in hours (to be passed as parameters of the cron job)
now = 1208649599000 
hours = 24
# download format for the images (png, jpg, eps, pdf...)
format = 'png'

CMDWGET = 'wget -p --convert-links -nH -nd -Pdownload '
URL_HOME = 'http://glast-ground.slac.stanford.edu/Reports/'
TIME_STR = '&timeInterval=%d-%d&maxBins=-1&imageFormat=%s' %(now-3600*1000*hours, now, format)

class report:
    def __init__(self):
        self.texFile = 'tex/report.tex'
        self.timeString = 'Time Interval (UTC):'
        self.texContent = '\documentclass[oneside,12pt,letterpaper]{report}\n'
        self.texContent += '\usepackage{graphicx}\n'
        self.texContent += '\usepackage{rotating}\n'
        self.texContent += '\\textwidth=19truecm\n \\textheight=23truecm\n'
        self.texContent += '\\oddsidemargin -1.0truecm\n'
        self.texContent += '\\begin{document}\n'
        self.texContent += '\pagestyle{empty}\n'
        self.urlist = []
        self.__reset()
        
    def __reset(self):
        os.system('rm -rf tex download')
        os.mkdir('tex')
        os.mkdir('download')
    
    def replist(self):
        os.system('%s "%s"' % (CMDWGET, URL_HOME))
        f = file('download/index.html')
        try:
            for line in f:
                if line.find("Panel") >= 0 and line.find("href") >=0:
                    self.urlist.append (line.split('\"')[1])
                if line.find("UTC") >=0:
                    self.timeString += line.split('>')[2]
        finally:
            f.close()

    def compile(self):
        self.texContent += '\end{center}\n'
        self.texContent += '\end{document}\n'
        f = file(self.texFile, 'w')
        f.write(self.texContent)
        f.close()
        os.system('cd tex; /opt/TWWfsw/bin/pdflatex report.tex')

class panel:                
    def __init__(self, link):
        self.link = link
        self.imgFilesList = []
        self.title = ''
        self.__reset()

    def __reset(self):
    	os.system('rm -rf download')
        os.mkdir('download')

    def download(self):
        URLDL = self.link + TIME_STR
        os.system('%s "%s"' % (CMDWGET, URLDL))

    def convert(self):
    	imgList = glob('./download/aida_plot*')
    	for img in imgList:
            name = img.split('=')[1].split('&')[0]+self.link.split('=')[1]+'.'+format
            self.imgFilesList.append(name)
            os.system('mv "%s" tex/%s' % (img, name))    
        g = file(glob('./download/report*')[0])
        try:
            for line in g:
                if line.find("h2") >= 0:
                    self.title = line.split('>')[1].split('<')[0]
        finally:
            g.close()
        if self.title.find("1") >= 0: 
            logoImg = 'glastLogo.png'
            os.system('mv "%s" tex/%s' % (glob('./download/*Reports')[0], logoImg))    
            r.texContent += '\\begin{figure}[t!]\n'
            r.texContent += '\includegraphics[width=4cm]{%s}\n' % logoImg
            r.texContent += '\end{figure}\n'
            r.texContent += '\\begin{center}\n'
            r.texContent += r.timeString + '\n'

    def doTex(self):
    	r.texContent += '\\begin{figure}[h!]\n'
       	r.texContent += '\\begin{minipage}[c]{0.05\linewidth}\n'
        r.texContent += '\\hspace*{-10pt}\\\\\n'
        r.texContent += '\\begin{sideways}'+self.title+'\end{sideways}\n'
        r.texContent += '\\hspace*{-10pt}\\\\\n'
       	r.texContent += '\end{minipage}\n'
       	r.texContent += '\\begin{minipage}[c]{0.95\linewidth}\n'
        #r.texContent += '\\begin{tabular}{|c|p{2cm}|}\n'
        r.texContent += '\\begin{tabular}{|c|}\n'
        r.texContent += '\hline\n'
        r.texContent += '\\vspace*{0pt}\\\\\n'

        for name in self.imgFilesList:
	        self.texAddImage(name)

        r.texContent += '\\vspace*{0pt}\\\\\n'
        r.texContent += '\hline\n'
        r.texContent += '\end{tabular}\n'
       	r.texContent += '\end{minipage}\n'
    	r.texContent += '\end{figure}\n'

    def texAddImage(self, name):
    	r.texContent += '  \includegraphics[width=16cm]{%s} \\\\ \n' % name
    	#r.texContent += '  \includegraphics[width=14cm,viewport=0 0 1003 126]{%s} \\\\ \n' % name
    	#r.texContent += '   & \\tiny{here will go the figure caption} \\\\ \n'
    	
    def get(self):
        self.download()
        self.convert()
        self.doTex()

if __name__ == '__main__':
    r = report()
    r.replist()
    for lk in r.urlist:
        p = panel(lk)
        p.get()
    r.compile()
    

