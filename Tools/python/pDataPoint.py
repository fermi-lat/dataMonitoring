

class pDataPoint:

    def __init__(self, timestamp, value, error):
        self.Timestamp = timestamp
        self.Value = value
        self.Error = error
        
    def isNull(self):
        return abs(self.Timestamp) < 5 and self.Value == 0 and self.Error == 0

    def getTextRepresentation(self):
        return '(t = %.1f, value = %.3f += %.3f)' %\
            (self.Timestamp, self.Value, self.Error)
       
    def __cmp__(self, other):
        return int(self.Timestamp - other.Timestamp)
 
    def __sub__(self, other):
        return pDataPoint(self.Timestamp - other.Timestamp,\
                              self.Value - other.Value,\
                              self.Error - other.Error)

    def __str__(self):
        return self.getTextRepresentation()
