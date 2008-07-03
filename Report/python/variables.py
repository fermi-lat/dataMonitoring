
import os

import config

prefix = config.nameManglingPrefix
def mangleName(fileType, name):
    mangledName = '_'.join([prefix, fileType, name])
    return mangledName

def setVar(fileType, name, value):
    import pipeline
    pipeline.setVariable(mangleName(fileType, name), value)
    return

def getVar(fileType, name):
    mangledName = '_'.join([prefix, fileType, name])
    value = os.environ[mangledName]
    return value

