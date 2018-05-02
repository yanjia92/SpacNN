class Simulator(object):
    def __init__(self, model):
        # model : instance of ModulesFile
        self.model = model

    def genPath(self, duration):
        return self.model.gen_random_path(duration)
