import os
import sys
import re
import logging

logging.basicConfig(level = logging.DEBUG)



class pReportPage:

    def __init__(self):
        self.PanelsList = []

    def addPanel(self, panel):
        self.PanelsList.append(panel)
