class Simulator(object):
    def __init__(self, model):
        # model : instance of type ModulesFile
        self.model = model

    def genPath(self, duration):
        return self.model.genRandomPath(duration)
