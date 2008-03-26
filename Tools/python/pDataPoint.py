

MAX_DISCREPANCY = 1.e-12

class pDataPoint:

    def __init__(self, timestamp, value, error):
        self.Timestamp = timestamp
        self.Value = value
        self.Error = error
        
    def isNull(self):
        return self.Timestamp == 0 and \
               abs(self.Value) < MAX_DISCREPANCY and \
               abs(self.Error) < MAX_DISCREPANCY

    def getTextRepresentation(self):
        return '(t = %d, value = %.10f += %.10f)' %\
               (self.Timestamp, self.Value, self.Error)
       
    def __cmp__(self, other):
        return int(self.Timestamp - other.Timestamp)
 
    def __sub__(self, other):
        return pDataPoint(self.Timestamp - other.Timestamp,\
                          self.Value - other.Value,\
                          self.Error - other.Error)

    def __str__(self):
        return self.getTextRepresentation()
