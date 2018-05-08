class ModelConstructor(object):
    def __init__(self, f):
        self._f =  f
        self.lines = []
        with open(self._f) as temp:
            for l in temp:
                self.lines.append(l)
        # print lines

def test():
    constructor = ModelConstructor("../../prism_model/NewModel.prism")
    
