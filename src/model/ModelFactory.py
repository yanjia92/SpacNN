from module.ModulesFile import ModulesFile, ModelType


class ModelFactory(object):
    def __init__(self, moduleFactory):
        self.modulefactory = moduleFactory

    def spsmodel(self):
        def failurecondition(vs, cs):
            return vs['sb_status'] == 0 or vs['s3r_status'] == 0
        labels = {}
        labels['up'] = lambda vs, cs: vs['s3r_status'] == 1 and vs['sb_status'] == 1
        labels['failure'] = lambda vs, cs: vs['s3r_status'] == 0 or vs['sb_status'] == 0
        model = ModulesFile(
            ModelType.DTMC,
            failureCondition=failurecondition,
            stopCondition=failurecondition,
            modules=[
                self.modulefactory.timermodule(),
                self.modulefactory.s3rmodule(),
                self.modulefactory.sbmodule()],
            labels=labels)
        model.constants['SCREEN_THICKNESS'] = self.modulefactory.config.getParam('SCREEN_THICKNESS')
        return model
