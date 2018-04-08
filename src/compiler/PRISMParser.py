import ply.yacc as yacc

from PRISMLex import MyLexer
tokens = MyLexer.tokens
from module.ModulesFile import ModulesFile, ModelType
from PRISMLex import MyLexer


class BasicParser(object):
    def p_model_type(self, p):
        '''model_type : dtmc | ctmc'''
        if self.model:
            self.model = ModulesFile([ModelType.DTMC, ModelType.CTMC]['ctmc' == p[1]])


    def p_const_expression(self, p):
        '''const_expression : const TYPE NAME ASSIGN VALUE'''
        self.checktype(p[2], p[len(p)-1])


    def checktype(self, type, value):
        pass

    def getModel(self, modelfile):
        lines = []
        with open(modelfile) as f:
            for l in f:
                lines.append(l)
        if self.parser:
            self.parser.parse(lines)
        if self.model:
            return self.model
        return None

    def build(self):
        self.parser =  yacc.yacc(module=self)
        if not self.model:
            self.model = ModulesFile()



class ModelConstructor(object):
    def __init__(self):
        self.lexer = MyLexer()
        self.parser = BasicParser()
        self.parser.build()

    def parseModelFile(self, modelfile):
        return self.parser.getModel(modelfile)

def testModelConstruction():
    constructor = ModelConstructor()
    model = constructor.parseModelFile("../../prism_model/smalltest.prism")
    print model.modelType

if __name__ == "__main__":
    testModelConstruction()