from module.ModulesFile import ModulesFile, ModelType
from compiler.PRISMParser import ModelConstructor
from model.ModuleFactory import ModuleFactory
from config.SPSConfig import SPSConfig
from PathHelper import get_proj_dir, get_sep


class ModelFactory(object):
    module_factory = ModuleFactory(SPSConfig())

    @classmethod
    def get_built(cls):
        def failurecondition(vs, cs):
            sb_status = vs['sb_status'].getValue()
            s3r_status = vs['s3r_status'].getValue()
            bcr_status = vs['bcr_status'].getValue()
            bdr_status = vs['bdr_status'].getValue()
            return (sb_status+s3r_status+bcr_status+bdr_status) < 4

        labels = {}
        labels['failure'] = failurecondition
        
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


    @classmethod
    def setParam(cls, name, value):
        if name not in cls.module_factory.config.params.keys():
            return
        cls.module_factory.config.setParam(name, value)


    @staticmethod
    def get_parsed():
        sep = get_sep()
        mdl_dir = sep.join((get_proj_dir(), 'prism_model', 'smalltest.prism'))
        return ModelConstructor().parseModelFile(mdl_dir)

