## @package pAlarmOutput
## @brief Module describing the output of an alarm.

import pSafeLogger
logger = pSafeLogger.getLogger('pAlarmOutput')

import pUtils
import pAlarm

STATUS_CLEAN     = {'level': 1, 'label': 'CLEAN'}
STATUS_WARNING   = {'level': 2, 'label': 'WARNING'}
STATUS_ERROR     = {'level': 3, 'label': 'ERROR'}
STATUS_UNDEFINED = {'level': 4, 'label': 'UNDEFINED'}
MAX_DETAIL_SIZE  = 500

## @brief Class describing the output of an alarm.
#
#  The output of an alarm consists of three main pieces:
#  @li an output value returned by a given algorithm.
#  @li a status resulting from the comparison of the value with the limits.
#  @li a detailed dictionary wich can be filled with arbitrary information
#  while the alarm algorithm is run on the ROOT object.
#
#  This class is responsible for checking the output value provided by
#  an algorithm against the alarm limits. This happens whenever the
#  setValue() method is called.

class pAlarmOutput:

    ## @brief Basic constructor.
    ## @param self
    #  The class instance.
    ## @param limits
    #  The alarm limits.
    
    def __init__(self, limits, parent):

        ## @var Limits
        ## @brief The alarm limits.

        ## @var Value
        ## @brief The algorithm output value.

        ## @var Label
        ## @brief A brief string representing the meaning of the output value.

        ## @var Status
        ## @brief The status label.

        ## @var DetailedDict
        ## @brief The dictionary containing the detailed information.
        
        self.Limits       = limits
        self.Parent       = parent
        self.Value        = None
        self.Label        = None
        self.Status       = STATUS_UNDEFINED
        self.Compressed   = False
        self.DetailedDict = {}
        self.ForceError   = False

    ## @brief Return whether the status is undefined or not.
    ## @param self
    #  The class instance.        

    def isUndefined(self):
        return self.Status == STATUS_UNDEFINED

    ## @brief Return whether the detailed output dictionary has been compressed
    #  or not.
    ## @param self
    #  The class instance. 

    def isCompressed(self):
        return self.Compressed

    ## @brief Return whether the status is clean or not.
    ## @param self
    #  The class instance.        

    def isClean(self):
        return self.Status == STATUS_CLEAN

    ## @brief Return whether the status is warning or not.
    ## @param self
    #  The class instance.        

    def isWarning(self):
        return self.Status == STATUS_WARNING

    ## @brief Return whether the status is error or not.
    ## @param self
    #  The class instance.        

    def isError(self):
        return self.Status == STATUS_ERROR

    ## @brief Set the output value and check it against the alarm limits.
    ## @param self
    #  The class instance.
    ## @param value
    #  The output value.
        
    def setValue(self, value, compress = True):
        self.Value = value
        self.__processValue()
        if compress:
            self.compress()

    def setStatusUndefined(self):
        self.Status = STATUS_UNDEFINED

    def setStatusClean(self):
        self.Status = STATUS_CLEAN

    def setStatusWarning(self):
        self.Status = STATUS_WARNING

    def setStatusError(self):
        self.Status = STATUS_ERROR

    ## @brief Check the output value against the limits.
    ## @param self
    #  The class instance.
    
    def __processValue(self):
        if self.Parent.Exception is None:
            flip = False
        else:
            flip = self.Parent.Exception.FlippedStatus
        if self.ForceError:
            self.setStatusError()
            self.Value = None
        elif self.Value is None:
            self.setStatusUndefined()
        elif (self.Value > self.Limits.WarningMin)\
                 and (self.Value < self.Limits.WarningMax):
            if flip:
                self.setStatusError()
                self.appendDictValue('exception violations', 'output_status')
            else:
                self.setStatusClean()
        elif (self.Value <= self.Limits.ErrorMin)\
                 or (self.Value >= self.Limits.ErrorMax):
            if flip:
                self.setStatusClean()
                self.appendDictValue('known_issues', 'output_status')
            else:
                self.setStatusError()
        else:
            if flip:
                self.setStatusClean()
                self.appendDictValue('known_issues', 'output_status')
            else:
                self.setStatusWarning()

    ## @brief Get the value corresponding to a particular key of the
    #  detailed dictionary.
    ## @param self
    #  The class instance.
    ## @param key
    #  The dictionary key.

    def getDictValue(self, key):
        return self.DetailedDict[key]

    ## @brief Set the value corresponding to a particular key of the
    #  detailed dictionary.
    ## @param self
    #  The class instance.
    ## @param key
    #  The dictionary key.
    ## @param value
    #  The dictionary value.

    def setDictValue(self, key, value):
        self.DetailedDict[key] = value

    ## @brief Increment the value corresponding to a particular key of the
    #  detailed dictionary by a specific amount.
    ## @param self
    #  The class instance.
    ## @param key
    #  The dictionary key.
    ## @param amount
    #  The amount.

    def incrementDictValue(self, key, amount = 1):
        self.DetailedDict[key] += amount

    ## @brief Append an element to a specific key of the detailed dictionary.
    ## @param self
    #  The class instance.
    ## @param key
    #  The dictionary key.
    ## @param value
    #  The value to append.

    def appendDictValue(self, key, value):
        try:
            self.DetailedDict[key].append(value)
        except KeyError:
            self.DetailedDict[key] = [value]

    ## @brief Return the output value, nicely formatted as a string.
    ## @param self
    #  The class instance. 

    def getFormattedValue(self):
        return pUtils.formatNumber(self.Value)

    ## @brief Compress the output detailed dictionary in order to avoid too
    #  much verbosity in the output xml file.
    ## @param self
    #  The class instance. 

    def compress(self):
        for (key, value) in self.DetailedDict.items():
            if len(str(value)) > MAX_DETAIL_SIZE:
                self.Compressed = True
                self.DetailedDict[key] = '%s... too much garbage following' %\
                    str(value)[:MAX_DETAIL_SIZE]

    ## @brief Return a string representation of the alarm output.
    ## @param self
    #  The class instance.
            
    def getTextSummary(self):
        summary = ''
        summary += 'Limits  : %s\n' % self.Limits
        summary += 'Output  : %s (%s)\n' %\
            (self.getFormattedValue(), self.Label)
        summary += 'Status  : %s\n' % self.Status
        summary += 'Details : %s\n' % self.DetailedDict
        return summary

    ## @brief Class representation.
    ## @param self
    #  The class instance.    

    def __str__(self):
        return self.getTextSummary()

    
if __name__ == '__main__':
    from pAlarmLimits import pAlarmLimits
    limits = pAlarmLimits(-1, 3, -1, 6)
    AlarmOutput = pAlarmOutput(limits)
    print AlarmOutput
    for i in range(1000):
        AlarmOutput.appendDictValue('test key', 'test string')
    print AlarmOutput
    AlarmOutput.setValue(100)
    print AlarmOutput

