# -*- coding: utf-8 -*-
import ply.yacc as yacc
from module.ModulesFile import *
from PRISMLex import MyLexer
from module.Module import *
from util.FuncUtil import *
from removeComment import clear_comment
from util.MathUtils import *
import logging

logger = logging.getLogger("PRISMParser logging")
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class ExpressionHelper(object):

    binary_op_map = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y
    }

    func_map = {
        'stdcdf': stdcdf,
        'log': log,
        'powe': powe
    }

    @classmethod
    def execbinary(cls, op, *params):
        func = cls.binary_op_map[op]
        return func(*params)

    @classmethod
    def execfunc(cls, func_name, *params):
        func = cls.func_map.get(func_name, None)
        if not func:
            raise Exception("Not supported function {}".format(func_name))
        return func(*params)

    @staticmethod
    def resolve_boolean_expression(val1, val2, op):
        # val1, val2 : number literal
        # op: > < >= <= == !=
        if '<' == op:
            return val1 < val2
        if '>' == op:
            return val1 > val2
        if '>=' == op:
            return val1 >= val2
        if '<=' == op:
            return val1 <= val2
        if '==' == op:
            return val1 == val2
        if '!=' == op:
            return val1 != val2


class BasicParser(object):
    def __init__(self):
        self.moduledefbegin = False  # 表示当前是否正在解析module模块
        '''
        当parser分析到一行Command时，可能最后会解析成多个Command对象
        每个Command对象包含以下信息：name, guard, prob, action, module
        目前默认不设置Command的name，即name为空
        module在每次解析到LB时进行初始化表示当前正在生成的module
        prob在解析到prob_expr的时候进行设置，prob是一个函数对象，因为需要根据判定对象（变量）的值进行实时计算
        最重要的Command对象在解析到prob_update时进行初始化，因为从Command的构成上讲，
        一个prob + update就构成了一个Command对象。
        之所以要在BasicParser中保存module和guard对象是因为
        它们是被多个Command对象所共享的。
        '''
        self.module = None  # 当前正在解析的module对象
        self.guard = None  # 表示当前Command对象的guard属性
        self.binary_op_map = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y
        }
        self.func_map = {
            'stdcdf': stdcdf
        }
        # name : value storage structure for constants
        self.cmap = {}
        # name : func object storage structure for variables and formula
        self.vfmap = {}

    def p_statement(self, p):
        '''statement : model_type_statement
                     | const_value_statement
                     | module_def_begin_statement
                     | module_def_end_statement
                     | module_var_def_statement
                     | module_command_statement
                     | formula_statement'''
        # print "slice: {}".format(p.slice)
        pass

    def p_model_type(self, p):
        '''model_type_statement : DTMC
                      | CTMC'''
        model_type = ModelType.CTMC
        if p[1] == 'dtmc':
            model_type = ModelType.DTMC
        ModelConstructor.model = ModulesFile.ModulesFile(modeltype=model_type)

    def p_module_def_begin_statement(self, p):
        '''module_def_begin_statement : MODULE NAME'''
        self.moduledefbegin = True
        self.module = Module(p[2])

    def p_module_def_end_statement(self, p):
        '''module_def_end_statement : ENDMODULE'''
        if self.moduledefbegin:
            self.moduledefbegin = False
            ModelConstructor.model.addModule(self.module)

    def p_const_expression(self, p):
        '''const_value_statement : CONST INT NAME ASSIGN NUM SEMICOLON
                                 | CONST DOUBLE NAME ASSIGN NUM SEMICOLON
                                 | CONST BOOL NAME ASSIGN NUM SEMICOLON'''
        name = p[3]
        value = self.resolvetype(p[5], p[2])
        obj = Constant(name, value)
        ModelConstructor.model.addConstant(name, obj)
        self.cmap[p[3]] = obj
        logger.info("Constant added: {} = {}".format(name, value))

    def p_const_expression1(self, p):
        '''const_value_statement : CONST INT NAME SEMICOLON
                             | CONST DOUBLE NAME SEMICOLON
                             | CONST BOOL NAME SEMICOLON'''
        # 支持解析不确定的常量表达式
        name = p[3]
        obj = Constant(name)
        ModelConstructor.model.addConstant(name, obj)
        self.cmap[name] = obj
        logger.info("Unspecified constant added: {}".format(name))

    def p_const_expression2(self, p):
        '''const_value_statement : CONST INT NAME ASSIGN expr SEMICOLON
                                 | CONST DOUBLE NAME ASSIGN expr SEMICOLON
                                 | CONST BOOL NAME ASSIGN expr SEMICOLON'''
        name = p[3]
        value = self.resolvetype(p[5](), p[2])
        obj = Constant(name, value)
        ModelConstructor.model.addConstant(name, obj)
        self.cmap[name] = obj
        logger.info("Constant added: {} = {}".format(name, value))

    def p_module_var_def_statement(self, p):
        '''module_var_def_statement : NAME COLON LB expr COMMA expr RB INIT NUM SEMICOLON'''
        #  让var的lowbound和upperbound支持expression
        tokens = copy.copy(p.slice)
        min = tokens[4].value()
        max = tokens[6].value()
        var = Variable(p[1], p[len(p) - 2], range(min, max + 1),
                       int)  # 目前默认变量的类型是int p[index] index不能是负数
        self.module.addVariable(var)
        self.vfmap[var.getName()] = lambda: ModelConstructor.model.getLocalVar(var.getName())
        logger.info("Variable_{} added to Module_{}. init={}, range=[{}, {}]".format(var.getName(), str(self.module), var.initVal, var.valRange[0], var.valRange[-1]))

    def p_module_command_statement(self, p):
        '''module_command_statement : LB RB boolean_expression THEN updates SEMICOLON'''
        print "command.tokens : {}".format(p.slice)

    def p_updates(self, p):
        '''updates : updates ADD prob_update'''
        pass

    def p_updates1(self, p):
        '''updates : prob_update'''
        pass

    def p_prob_update(self, p):
        '''prob_update : expr COLON actions'''
        prob = p[1]  # prob_expr is a function
        action = p[3]  # actions is a function
        command = Command("", self.guard, action, self.module, prob)
        self.module.addCommand(command)
        print "Command added."

    def p_actions(self, p):
        '''actions : actions AND assignment'''
        f1 = p[1]
        f2 = p[3]

        def f():
            f1()
            f2()

        p[0] = f

    def p_actions2(self, p):
        '''actions : assignment'''
        p[0] = p[1]  # a assignment is a function that udpate the variable in model.localVars

    def p_assignment(self, p):
        '''assignment : NAME ASSIGN expr'''
        update_func = copy.deepcopy(p[3])
        var_name = copy.copy(p[1])

        def f(vs, cs):
            var = vs[var_name]
            if not var or not isinstance(var, Variable):
                raise Exception("invalid variable name")
            var.setValue(update_func())

        p[0] = f

    def p_assignment1(self, p):
        '''assignment : LP NAME ASSIGN expr RP'''
        update_func = copy.deepcopy(p[4])
        key = p[2]

        def f(vs, cs):
            var = vs[key]
            if not var or not isinstance(var, Variable):
                raise Exception("invalid variable name: {}".format(key))
            var.setValue(update_func())

        p[0] = f

    def p_expr(self, p):
        '''expr : expr ADD term
                | expr MINUS term'''
        func = self.binary_op_map[p[2]]
        slice_copy = copy.deepcopy(p.slice)

        def f():
            return func(slice_copy[1].value(), slice_copy[3].value())

        p[0] = f

    def p_expr2(self, p):
        '''expr : term'''
        p[0] = p[1]

    # def p_expr3(self, p):
    #     '''expr : LP expr RP'''
    #     p[0] = p[2]

    def p_term(self, p):
        '''term : term MUL factor
                | term DIV factor'''
        func = self.binary_op_map[p[2]]
        slice_copy = copy.deepcopy(p.slice)

        def f():
            return func(slice_copy[1].value(), slice_copy[3].value())
        p[0] = f

    def p_term1(self, p):
        '''term : factor'''
        p[0] = p[1]

    # def p_term2(self, p):
    #     '''term : LP expr RP'''
    #     p[0] = p[2]

    def p_factor(self, p):
        '''factor : NUM'''
        num = p[1]
        p[0] = lambda: num

    def p_factor1(self, p):
        '''factor : NAME'''
        slice_cpy = copy.copy(p.slice)
        name = slice_cpy[1].value

        def f():
            if name in ModelConstructor.model.localVars.keys():
                return ModelConstructor.model.getLocalVar(name).getValue()
            if name in ModelConstructor.model.constants.keys():
                return ModelConstructor.model.getConstant(name).getValue()
            # name refers to a formula
            return self.vfmap[name]()
        p[0] = f

    def p_factor2(self, p):
        '''factor : NAME LP expr RP'''
        slice = copy.copy(p.slice)
        func = ExpressionHelper.func_map.get(slice[1].value, None)
        if not func:
            raise Exception("Not supported function {}".format(slice[1].value))
        p[0] = lambda: func(slice[3].value())

    def p_factor3(self, p):
        '''factor : LP expr RP'''
        p[0] = p[2]

    def p_boolean_expression(self, p):
        '''boolean_expression : boolean_expression AND boolean_expression_unit
                              | boolean_expression OR boolean_expression_unit
                              | boolean_expression_unit'''
        print "boolean_expression detached."
        if len(p) == 4:
            if p[2] == "&":
                def f():
                    return p[1]() and p[3]()
            if p[2] == "|":
                def f():
                    return p[1]() or p[3]()
            p[0] = f
        elif len(p) == 2:
            p[0] = p[1]
        self.guard = p[0]
        # print self.guard

    def p_boolean_expression_unit(self, p):
        '''boolean_expression_unit : NAME GT NUM
                                   | NAME LT NUM
                                   | NAME GE NUM
                                   | NAME LE NUM
                                   | NAME EQ NUM
                                   | NAME NEQ NUM'''
        # 解析单个变量与某个常量进行比较
        tokens = copy.copy(p.slice)

        def f(t, handler):
            def inner(vs, cs):
                var = vs[t[1].value]
                if not var or not isinstance(var, Variable):
                    raise Exception("invalid variable name")
                left = var.getValue()
                right = t[3]
                op = t[2]
                print str(left) + str(op) + str(right)
                return handler(left, right, op)

            return inner

        p[0] = f(tokens, ExpressionHelper.resolve_boolean_expression)
        print "guard find : {} == {}".format(tokens[1].value, tokens[3])

    def p_boolean_expression_unit1(self, p):
        '''boolean_expression_unit : NAME GT expr
                                   | NAME LT expr
                                   | NAME GE expr
                                   | NAME LE expr
                                   | NAME EQ expr
                                   | NAME NEQ expr'''
        # 解析某个变量与一个表达式进行比较
        tokens = copy.copy(p.slice)

        def f(t, handler):
            # handler is a boolean_expression_resolver : handler(val1, val2,
            # op)
            def inner(vs, cs):
                var = vs[t[1].value]
                if not var or not isinstance(var, Variable):
                    raise Exception("invalid var name")
                left = var.getValue()
                right = t[3].value()
                op = t[2].value
                return handler(left, right, op)

            return inner

        p[0] = f(tokens, ExpressionHelper.resolve_boolean_expression)

    def p_formula_statement(self, p):
        '''formula_statement : FORMULA NAME ASSIGN expr SEMICOLON'''
        slices = copy.copy(p.slice)
        frml_name = slices[2].value
        self.vfmap[frml_name] = slices[4].value
        logger.info("Formula_{} added.".format(slices[2].value))

    def checktype(self, type, value):
        return True

    def resolvetype(self, strval, type):
        if 'int' == type:
            return int(strval)
        if 'double' == type:
            return float(strval)
        if 'bool' == type:
            return bool(strval)

    def resolvenum(self, strval):
        if strval.find(r"\.") == -1:
            return int(strval)
        return float(strval)

    def parse_model(self, filepath):
        commentremoved = clear_comment(filepath)
        print "Parsing model file : {}".format(commentremoved)
        lines = []

        with open(commentremoved) as f:
            for l in f:
                lines.append(l)
        if self.parser:
            myLexer = MyLexer()
            lexer = myLexer.lexer
            for line in lines:
                tokens = []
                if line.find("[]") != -1:
                    lexer.input(line)
                    for token in lexer:
                        tokens.append(token)
                    print tokens
                self.parser.parse(line, lexer=lexer)


    def build(self):
        self.tokens = MyLexer.tokens
        self.parser = yacc.yacc(module=self, debug=1)


class ModelConstructor(object):
    model = None

    def __init__(self):
        self.parser = BasicParser()
        self.parser.build()
        ModelConstructor.model = ModulesFile.ModulesFile(ModelType.DTMC)

    def parseModelFile(self, filepath):
        self.parser.parse_model(filepath)
        return ModelConstructor.model


def testModelConstruction():
    constructor = ModelConstructor()
    model = constructor.parseModelFile("../../prism_model/smalltest.prism")
    print model.modules.values()[0].commands

if __name__ == "__main__":
    testModelConstruction()
