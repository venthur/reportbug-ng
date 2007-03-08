
class Bugreport:
    """Represents a Bugreport from Debians BTS."""
    
    def __init__(self, nr, summary="", submitter="", status="", severity="", fulltext=""):
        self.nr = nr
        self.summary = summary
        self.submitter = submitter
        self.status = status
        self.severity = severity
        self.fulltext = fulltext

    def __str__(self):
        tmp = "#"+str(self.nr) +": "+ str(self.summary)
        return tmp
    