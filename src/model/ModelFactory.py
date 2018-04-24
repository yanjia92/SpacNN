from module.ModulesFile import ModulesFile, ModelType
from compiler.PRISMParser import ModelConstructor
from model.ModuleFactory import ModuleFactory
from config.SPSConfig import SPSConfig


class ModelFactory(object):
    module_factory = ModuleFactory(SPSConfig())

    @classmethod
    def get_built(cls):
        def failurecondition(vs, cs):
            return vs['sb_status'] == 0 or vs['s3r_status'] == 0 or vs["bcr_status"] == 0 and vs["bdr_status"] == 0
        labels = {}
        labels['up'] = lambda vs, cs: vs['s3r_status'] == 1 and vs['sb_status'] == 1 and vs["bcr_status"] == 1 and vs["bdr_status"] == 1
        labels['failure'] = lambda vs, cs: vs['s3r_status'] == 0 or vs['sb_status'] == 0 or vs["bcr_status"] == 0 and vs["bdr_status"] == 0
        model = ModulesFile(
            ModelType.DTMC,
            failureCondition=failurecondition,
            stopCondition=failurecondition,
            modules=[
                cls.module_factory.timermodule(),
                cls.module_factory.s3rmodule(),
                cls.module_factory.sbmodule(),
                cls.module_factory.bcrmodule(),
                cls.module_factory.bdrmodule()],
            labels=labels)
        model.constants['SCREEN_THICKNESS'] = cls.module_factory.config.getParam('SCREEN_THICKNESS')
        return model

    @staticmethod
    def get_parsed():
        mdl_dir = "../../prism_model/smalltest.prism"
        return ModelConstructor().parseModelFile(mdl_dir)

