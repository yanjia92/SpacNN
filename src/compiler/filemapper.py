class FileMapper(object):
    def __init__(self, filename):
        # filename: absolute path of file
        self.filename = filename
        self._f = open(filename, "r")
        self.lines = []
        for line in self._f:
            self.lines.append(line)
    
    def map(self, mapper):
        # mapper: func object f(str) -> str
        for i, l in enumerate(self.lines):
            self.lines[i] = mapper(l)

    def write2(self, dest=""):
        if len(dest) == 0:
            

