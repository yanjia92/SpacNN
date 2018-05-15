from module.ModulesFile import ModulesFile, ModelType
from compiler.PRISMParser import ModelConstructor
from model.ModuleFactory import ModuleFactory
from config.SPSConfig import SPSConfig
from PathHelper import get_proj_dir, get_sep


class ModelFactory(object):
    module_factory = ModuleFactory(SPSConfig())
    model_constructor = ModelConstructor()

    @classmethod
    def get_built(cls):
        def failurecondition(vs, cs):
            sb_status = vs['sb_status'].get_value()
            s3r_status = vs['s3r_status'].get_value()
            bcr_status = vs['bcr_status'].get_value()
            bdr_status = vs['bdr_status'].get_value()
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
        model.duration = 730
        return model



    @classmethod
    def setParam(cls, name, value):
        if name not in cls.module_factory.config.params.keys():
            return
        cls.module_factory.config.setParam(name, value)


    @classmethod
    def get_parsed(cls, duration=730):
        sep = get_sep()
        mdl_dir = sep.join((get_proj_dir(), 'prism_model', 'smalltest.prism'))
        model =  cls.model_constructor.parseModelFile(mdl_dir)
        model.duration = duration
        return model

