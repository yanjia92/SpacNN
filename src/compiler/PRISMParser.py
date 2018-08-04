# -*- coding: utf-8 -*-

import ply.yacc as yacc
from PRISMLex import MyLexer
from module.ModulesFile import *
from module.Module import *
from removeComment import clear_comment
from util.MathUtils import *
from collections import defaultdict
from util.ListUtils import shallow_cpy
from math import floor, ceil


def bin_add(x,y):
    '''bin_add'''
    return x+y


def bin_minus(x, y):
    '''bin_minus'''
    return x - y


def bin_times(x, y):
    '''bin times'''
    return x * y


def bin_div(x, y):
    '''bin divide'''
    return x / y


class ExpressionHelper(object):

    binary_op_map = {
        '+': bin_add,
        '-': bin_minus,
        '*': bin_times,
        '/': bin_div,
    }

    func_map = {
        'stdcdf': pcf,
        'log': log,
        'powe': powe,
        'min': min,
        'max': max,
        'floor': int,
        'ceil': int
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
    FRML_FUNC_PREFIX = "FRML"
    VAR_FUNC_PREFIX = "VAR"
    SPLIT = ":"

    def __init__(self):
        # 表示当前是否正在解析module模块
        # 用途: 值为false时,对boolean_expression的解析不会将结果保存为guard
        self.moduledefbegin = False
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
            'stdcdf': pcf,
            'floor' : floor,
            'ceil'  : ceil
        }
        # when parsing a command declaration, store the command sync_name in this property
        self.comm_name = None
        # name : value storage structure for constants
        # name : func object storage structure for variables and formula
        # self.logger = logging.getLogger("BasicParser logging")
        # self.logger.addHandler(logging.FileHandler(LogHelper.get_logging_root() + "BasicParser.log"))
        # self.logger.setLevel(logging.ERROR)
        self.vcf_map = defaultdict(lambda: None)

    def constname_unsure(self):
        ''':return 不确定的常量名 [str]'''
        names = []
        for name, obj_or_func in self.vcf_map.items():
            if not callable(obj_or_func):
                if obj_or_func.get_value() is None:
                    # unsure Constant objects
                    names.append(name)
        return names

    def p_statement(self, p):
        '''statement : model_type_statement
                     | const_value_statement
                     | module_def_begin_statement
                     | module_def_end_statement
                     | module_var_def_statement
                     | module_command_statement
                     | formula_statement
                     | label_statement'''
        # print "slice: {}".format(p.slice)
        pass

    def p_model_type(self, p):
        '''model_type_statement : DTMC
                      | CTMC'''
        model_type = ModelType.CTMC
        if p[1] == 'dtmc':
            model_type = ModelType.DTMC
        ModelConstructor.model = ModulesFile(modeltype=model_type)

    def p_module_def_begin_statement(self, p):
        '''module_def_begin_statement : MODULE NAME'''
        self.moduledefbegin = True
        self.module = Module(p[2])

    def p_module_def_end_statement(self, p):
        '''module_def_end_statement : ENDMODULE'''
        if self.moduledefbegin:
            self.moduledefbegin = False
            ModelConstructor.model.add_module(self.module)
        else:
            # todo throw syntax error message
            pass

    def p_const_expression(self, p):
        '''const_value_statement : CONST INT NAME ASSIGN NUM SEMICOLON
                                 | CONST DOUBLE NAME ASSIGN NUM SEMICOLON
                                 | CONST BOOL NAME ASSIGN NUM SEMICOLON'''
        name = p[3]
        _value = p[5]
        _type = p[2]
        value = self.resolvetype(_value, _type)
        if not value:
            # todo log unrecognized type name
            pass
        obj = Constant(name, value)
        ModelConstructor.model.setConstant(name, obj)
        self.vcf_map[p[3]] = obj

    def p_const_expression1(self, p):
        '''const_value_statement : CONST INT NAME SEMICOLON
                             | CONST DOUBLE NAME SEMICOLON
                             | CONST BOOL NAME SEMICOLON'''
        # 支持解析不确定的常量表达式
        name = p[3]
        obj = Constant(name)
        ModelConstructor.model.setConstant(name, obj)
        self.vcf_map[name] = obj

    def p_const_expression2(self, p):
        '''const_value_statement : CONST INT NAME ASSIGN expr SEMICOLON
                                 | CONST DOUBLE NAME ASSIGN expr SEMICOLON
                                 | CONST BOOL NAME ASSIGN expr SEMICOLON'''
        name = p[3]
        value = self.resolvetype(p[5](), p[2])
        obj = Constant(name, value)
        ModelConstructor.model.setConstant(name, obj)
        self.vcf_map[name] = obj

    def p_module_var_def_statement(self, p):
        '''module_var_def_statement : NAME COLON LB expr COMMA expr RB INIT NUM SEMICOLON'''
        #  让var的lowbound和upperbound支持expression
        tokens = shallow_cpy(p.slice)
        min = tokens[4].value()
        max = tokens[6].value()
        var = Variable(p[1], p[len(p) - 2], range(min, max + 1),
                       int)  # 目前默认变量的类型是int p[index] index不能是负数
        self.module.addVariable(var)
        self.vcf_map[var.get_name()] = var

    def p_module_command_statement(self, p):
        '''module_command_statement : LB NAME RB boolean_expression THEN updates SEMICOLON'''
        sync_name = p[2]
        commands = p[6]
        for comm in commands:
            comm.name = sync_name
            self.module.addCommand(comm)

    def p_module_command_statement1(self, p):
        '''module_command_statement : LB RB boolean_expression THEN updates SEMICOLON'''
        sync_name = ""
        commands = p[5]
        for comm in commands:
            comm.name = sync_name
            self.module.addCommand(comm)

    def p_updates(self, p):
        '''updates : updates ADD prob_update'''
        p[0] = list()
        p[1].append(p[3])
        p[0].extend(p[1])

    def p_updates1(self, p):
        '''updates : prob_update'''
        p[0] = list()
        p[0].append(p[1])

    def p_prob_update(self, p):
        '''prob_update : expr COLON actions'''
        prob = p[1]  # prob_expr is a function
        actions = p[3]  # actions is a dict
        guard = copy.copy(self.guard)
        command = Command("", guard, actions, self.module, prob)
        p[0] = command

    def p_prob_update1(self, p):
        '''prob_update : actions'''
        prob = lambda : 1.0 # in CTMC, a prob can be default(not written) equals 1(it must be callable)
        actions = p[1]
        guard = copy.copy(self.guard)
        command = Command("", guard, actions, self.module, prob)
        p[0] = command

    def p_prob_update2(self, p):
        '''prob_update : TRUE'''
        prob = lambda : 1.0
        actions = dict()
        guard = copy.copy(self.guard)
        command = Command("", guard, actions, self.module, prob)
        p[0] = command

    def p_actions(self, p):
        '''actions : actions AND assignment'''
        tokens = shallow_cpy(p.slice)
        action1 = tokens[1].value  # dict
        action2 = tokens[3].value   # dict
        action2.update(action1)
        p[0] = action2

    def p_actions2(self, p):
        '''actions : assignment'''
        p[0] = p[1]  # a assignment is a function that udpate the variable in model.localVars

    def p_assignment(self, p):
        '''assignment : NAME QUOTE ASSIGN expr'''
        update_func = copy.deepcopy(p[4])
        var_name = copy.copy(p[1])

        p[0] = {self.vcf_map[var_name]: update_func}

    def p_assignment1(self, p):
        '''assignment : LP NAME QUOTE ASSIGN expr RP'''
        update_func = copy.copy(p[5])
        var_name = p[2]

        p[0] = {self.vcf_map[var_name]: update_func}

    def p_expr(self, p):
        '''expr : expr ADD term
                | expr MINUS term'''
        slice_copy = shallow_cpy(p.slice)
        op = slice_copy[2].value

        def f():
            '''binary expression function'''
            v1 = slice_copy[1].value()
            v2 = slice_copy[3].value()
            if op == '-':
                return v1 - v2
            else:
                return v1 + v2
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
        slice_copy = shallow_cpy(p.slice)
        op = slice_copy[2].value

        def f():
            v1 = slice_copy[1].value()
            v2 = slice_copy[3].value()
            if op == "*":
                return v1 * v2
            else:
                return v1 / v2
        p[0] = f

    def p_term1(self, p):
        '''term : factor'''
        p[0] = p[1]

    def p_factor(self, p):
        '''factor : NUM'''
        num = p[1]

        def f():
            return num
        f.func_doc = "return {}".format(str(num))
        p[0] = f

    def p_factor1(self, p):
        '''factor : NAME'''
        slice_cpy = shallow_cpy(p.slice)
        name = slice_cpy[1].value

        def f():
            obj = self.vcf_map[name]
            if not obj:
                # todo log unknown token name
                print name
            if callable(obj):
                try:
                    return obj()
                except ZeroDivisionError:
                    print name
            else:
                # constant or variable
                return obj.get_value()
        p[0] = f

    def p_factor2(self, p):
        '''factor : NAME LP expr RP'''
        slice = shallow_cpy(p.slice)
        func = ExpressionHelper.func_map.get(slice[1].value, None)
        # if not func:
        #     raise Exception("Not supported function {}".format(slice[1].value))

        def f():
            assert callable(func)
            return func(slice[3].value())
        f.func_doc = "func_{}".format(func.__name__)
        p[0] = f

    def p_factor3(self, p):
        '''factor : LP expr RP'''
        p[0] = p[2]

    def p_factor4(self, p):
        '''factor : NAME LP params RP'''
        func = ExpressionHelper.func_map.get(p[1], None)
        slice = shallow_cpy(p.slice)

        def f():
            params = [f() for f in slice[3].value]
            return func(*tuple(params))
        p[0] = f

    def p_params(self, p):
        '''params : params COMMA expr'''
        p[1].append(p[3])
        p[0] = p[1]

    def p_params1(self, p):
        '''params : expr'''
        p[0] = list()
        p[0].append(p[1]) # directly append function to list

    def p_boolean_expression(self, p):
        '''boolean_expression : boolean_expression AND boolean_expression_unit
                              | boolean_expression OR boolean_expression_unit
                              | boolean_expression_unit'''
        # print "boolean_expression detached."
        slices = shallow_cpy(p.slice)
        if len(slices) == 4:
            if slices[2].value == "&":
                def f(vs, cs):
                    return slices[1].value(vs, cs) and slices[3].value(vs, cs)
            if slices[2].value == "|":
                def f(vs, cs):
                    return slices[1].value(vs, cs) or slices[3].value(vs, cs)

            p[0] = f
        elif len(p) == 2:
            p[0] = p[1]
        if self.moduledefbegin:
            # 如果当前正在解析command
            # 否则要么是解析formula,要么是label
            self.guard = p[0]

    def p_boolean_expression_unit(self, p):
        '''boolean_expression_unit : NAME GT NUM
                                   | NAME LT NUM
                                   | NAME GE NUM
                                   | NAME LE NUM
                                   | NAME EQ NUM
                                   | NAME NEQ NUM'''
        # 解析单个变量与某个常量进行比较
        tokens = shallow_cpy(p.slice)
        op = copy.deepcopy(tokens[2])

        def f(tokens, op_token):
            def inner(vs ,cs):
                var = vs[tokens[1].value]
                # if not var or not isinstance(var, Variable):
                #     raise Exception("invalid variable name")
                val1 = var.get_value()
                val2 = tokens[3]
                op = op_token.value
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

            return inner

        p[0] = f(tokens, op)

    def p_boolean_expression_unit1(self, p):
        '''boolean_expression_unit : NAME GT expr
                                   | NAME LT expr
                                   | NAME GE expr
                                   | NAME LE expr
                                   | NAME EQ expr
                                   | NAME NEQ expr'''
        # 解析某个变量与一个表达式进行比较
        # 一个重大bug
        # 因为slice是list,所以在进行copy的时候不会对每个元素进行拷贝
        tokens = shallow_cpy(p.slice)
        optoken = copy.deepcopy(tokens[2])

        def f(t, op_token):
            def inner(vs, cs):
                var = vs[t[1].value]
                val1 = var.get_value()
                val2 = t[3].value()
                op = op_token.value
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
            return inner

        p[0] = f(tokens, optoken)

    def p_boolean_expression_unit2(self, p):
        '''boolean_expression_unit : TRUE'''
        p[0] = lambda vs, cs: True

    def p_boolean_expression_unit3(self, p):
        '''boolean_expression_unit : FALSE'''
        p[0] = lambda vs, cs: False

    def p_formula_statement(self, p):
        '''formula_statement : FORMULA NAME ASSIGN expr SEMICOLON'''
        slices = shallow_cpy(p.slice)
        frml_name = slices[2].value
        self.vcf_map[frml_name] = slices[4].value
        # self.logger.info("Formula_{} added.".format(slices[2].value))

    def p_label_statement(self, p):
        '''label_statement : LABEL NAME ASSIGN boolean_expression SEMICOLON'''
        lbl_name = p[2]
        lbl_func = p[4]
        ModelConstructor.model.labels[lbl_name] = lbl_func

    def resolvetype(self, strval, type):
        type_map = {"int": int, "double": float, "bool": bool}
        if type in type_map:
            return type_map[type](strval)
        else:
            return None

    def resolvenum(self, strval):
        if strval.find(r"\.") == -1:
            return int(strval)
        return float(strval)

    def parse_model(self, filepath):
        commentremoved = clear_comment(filepath)
        # self.logger.info("Parsing model file : {}".format(commentremoved))
        lines = []

        with open(commentremoved) as f:
            for l in f:
                lines.append(l)
        if self.parser:
            myLexer = MyLexer()
            lexer = myLexer.lexer
            for line in lines:
                # tokens = []
                # if line.find("[]") != -1:
                    # lexer.input(line)
                    # for token in lexer:
                    #     tokens.append(token)
                    # print tokens
                self.parser.parse(line, lexer=lexer)

    def build(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        self.tokens = MyLexer.tokens
        self.parser = yacc.yacc(module=self, outputdir=cur_dir)


class ModelConstructor(object):
    model = None

    def __init__(self):
        self.parser = BasicParser()
        self.parser.build()
        ModelConstructor.model = ModulesFile(ModelType.DTMC)
        # self.logger = logging.getLogger("model_constructor's logger")
        # self.logger.addHandler(logging.StreamHandler(sys.stdout))
        # self.logger.setLevel(logging.INFO)

    def parseModelFile(self, filepath):
        self.parser.parse_model(filepath)
        # self.logger.info("Model parsing finished.")
        print "Parse finished."
        return ModelConstructor.model


if __name__ == "__main__":
    modelConstructor = ModelConstructor()
    model = modelConstructor.parseModelFile("/Users/bitbook/Documents/SpacNN/prism_model/DPM.prism")


