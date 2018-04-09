import ply.yacc as yacc

from module.ModulesFile import ModulesFile, ModelType
from PRISMLex import MyLexer


class BasicParser(object):
    def p_statement(self, p):
        '''statement : model_type_statement
                     | const_value_statement'''

    def p_model_type(self, p):
        '''model_type_statement : DTMC
                      | CTMC'''
        if not self.model:
            if 'dtmc' == p[0]:
                self.model = ModulesFile(ModelType.DTMC)
            else:
                self.model = ModulesFile(ModelType.CTMC)
        else:
            self.model.modelType = [1,0]['dtmc' == p[1]]

    def p_const_expression(self, p):
        '''const_value_statement : CONST TYPE NAME ASSIGN NUM SEMICOLON'''
        if not self.checktype(p[2], p[5]):
            print "type error in {}".format(p)
        self.model.addConstant(p[3], self.resolvetype(p[5], p[2]))

    def checktype(self, type, value):
        return True

    def resolvetype(self, strval, type):
        if 'int' == type:
            return int(strval)
        if 'double' == type:
            return float(strval)
        if 'bool' == type:
            return bool(strval)

    def getModel(self, modelfile):
        lines = []
        with open(modelfile) as f:
            for l in f:
                lines.append(l)
        if self.parser:
            myLexer = MyLexer()
            myLexer.build()
            lexer = myLexer.lexer
            for line in lines:
                self.parser.parse(line, lexer=lexer)
        if self.model:
            return self.model
        return None

    def build(self):
        self.tokens = MyLexer.tokens
        self.parser = yacc.yacc(module=self)
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
    print "modeltype : {}".format(model.modelType)
    print "constants in model : {}".format(model.constants)

if __name__ == "__main__":
    testModelConstruction()