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
import logging, sys
from os.path import *
from copy import copy


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


class PRISMParser(object):

    def __init__(self):
        # 表示当前是否正在解析module模块
        # 用途: 值为false时,对boolean_expression的解析不会将结果保存为guard
        self._parsing_module = False
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
        self._m = None  # module
        self._g = None  # guard
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
        self._type_map = {
            'int': int,
            'double': float,
            'bool': bool
        }
        self._cname = None # command sync name
        self._vcf_map = defaultdict(lambda: None)  # variable, constant and function map

    def unsure_parameters(self):
        names = []
        for name, obj_or_func in self._vcf_map.items():
            if not callable(obj_or_func):
                if obj_or_func.get_value() is None:
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
        pass

    def p_model_type(self, p):
        '''model_type_statement : DTMC
                      | CTMC'''
        model_type = [ModelType.DTMC, ModelType.CTMC][p[1] == 'ctmc']
        ModelConstructor.set_model(ModulesFile(model_type=model_type))

    def p_module_def_begin_statement(self, p):
        '''module_def_begin_statement : MODULE NAME'''
        self._parsing_module = True
        self._m = Module(p[2])

    def p_module_def_end_statement(self, p):
        '''module_def_end_statement : ENDMODULE'''
        if not self._parsing_module:
            raise Exception("Syntax error: end module definition before starting defining it")
        self._parsing_module = False
        ModelConstructor.get_model().add_module(self._m)

    def p_const_expression(self, p):
        '''const_value_statement : CONST INT NAME ASSIGN NUM SEMICOLON
                                 | CONST DOUBLE NAME ASSIGN NUM SEMICOLON
                                 | CONST BOOL NAME ASSIGN NUM SEMICOLON'''
        n = p[3]
        v = self._resolve_literal(p[5], p[2])
        c = Constant(n, v, self._type_map[p[2]])
        ModelConstructor.get_model().add_constant(c)
        self._vcf_map[n] = c

    def p_const_expression1(self, p):
        '''const_value_statement : CONST INT NAME SEMICOLON
                             | CONST DOUBLE NAME SEMICOLON
                             | CONST BOOL NAME SEMICOLON'''
        # 支持解析不确定的常量表达式
        n = p[3]
        c = Constant(n, None, self._type_map[p[2]])
        ModelConstructor.get_model().add_constant(c)
        self._vcf_map[n] = c

    def p_const_expression2(self, p):
        '''const_value_statement : CONST INT NAME ASSIGN expr SEMICOLON
                                 | CONST DOUBLE NAME ASSIGN expr SEMICOLON
                                 | CONST BOOL NAME ASSIGN expr SEMICOLON'''
        n = p[3]
        expr = copy(p[5])
        t = copy(p[2]) # type

        # there could be unsure parameter in expression
        def f():
            v = self._resolve_literal(expr(), t)
            return v

        c = Constant(n, f, self._type_map[t])
        ModelConstructor.get_model().add_constant(c)
        self._vcf_map[n] = c

    def p_module_var_def_statement(self, p):
        '''module_var_def_statement : NAME COLON LB expr COMMA expr RB INIT expr SEMICOLON'''
        v = BoundedIntegerVariable(p[1], p[9], (p[4], p[6]))
        self._m.add_variable(v)
        self._vcf_map[v.get_name()] = v

    def p_module_command_statement(self, p):
        '''module_command_statement : LB NAME RB boolean_expression THEN updates SEMICOLON'''
        n = p[2]
        commands = p[6]
        for c in commands:
            c.set_name(n)
            c.set_module(self._m)
            self._m.add_command(c)

    def p_module_command_statement1(self, p):
        '''module_command_statement : LB RB boolean_expression THEN updates SEMICOLON'''
        n = ""
        commands = p[5]
        for c in commands:
            c.set_name(n)
            c.set_module(self._m)
            self._m.add_command(c)

    def p_updates(self, p):
        '''updates : updates ADD prob_update'''
        p[0] = list(p[1])
        p[0].append(p[3])

    def p_updates1(self, p):
        '''updates : prob_update'''
        p[0] = list()
        p[0].append(p[1])

    def p_prob_update(self, p):
        '''prob_update : expr COLON actions'''
        p[0] = Command(None, copy(self._g), p[1], p[3])

    def p_prob_update1(self, p):
        '''prob_update : actions'''
        # todo why copy here?
        p[0] = Command(None, copy(self._g), lambda :1.0, p[1])

    def p_prob_update2(self, p):
        '''prob_update : TRUE'''
        p[0] = Command(None, copy(self._g), lambda :1.0, dict())

    def p_actions(self, p):
        '''actions : actions AND assignment'''
        p[1].update(p[3])
        p[0] = p[1]

    def p_actions2(self, p):
        '''actions : assignment'''
        p[0] = p[1]

    def p_assignment(self, p):
        '''assignment : NAME QUOTE ASSIGN expr'''
        p[0] = {self._vcf_map[p[1]]: p[4]}

    def p_assignment1(self, p):
        '''assignment : LP NAME QUOTE ASSIGN expr RP'''
        p[0] = {self._vcf_map[p[2]]: p[5]}

    def p_assignment2(self, p):
        '''assignment : TRUE'''
        p[0] = {}

    def p_expr(self, p):
        '''expr : expr ADD term
                | expr MINUS term'''
        f1 = copy(p[1])
        f2 = copy(p[3])
        op = copy(p[2])

        def f():
            if not callable(f1) or not callable(f2):
                raise Exception("Expression must be a function")
            if op == '-':
                return f1() - f2()
            elif op == '+':
                return f1() + f2()
            raise Exception("Unrecognized operator {}".format(p[2]))
        p[0] = f

    def p_expr2(self, p):
        '''expr : term'''
        p[0] = copy(p[1])

    # def p_expr3(self, p):
    #     '''expr : LP expr RP'''
    #     p[0] = p[2]

    def p_term(self, p):
        '''term : term MUL factor
                | term DIV factor'''
        f1 = copy(p[1])
        f2 = copy(p[3])
        op = copy(p[2])

        def f():
            if not callable(f1) or not callable(f2):
                raise Exception("Expression must be a function")
            if op == "*":
                return f1() * f2()
            elif op == '/':
                return f1() / f2()
            raise Exception("Unrecognized operator {}".format(op))
        p[0] = f

    def p_term1(self, p):
        '''term : factor'''
        p[0] = copy(p[1])

    def p_factor(self, p):
        '''factor : NUM'''
        num = copy(p[1])
        p[0] = lambda : num

    def p_factor1(self, p):
        '''factor : NAME'''
        k = copy(p[1])

        def f():
            if k not in self._vcf_map:
                raise Exception("Unknown token {}".format(k))
            v = self._vcf_map[k]
            if callable(v):
                return v()
            return v.get_value()
        p[0] = f

    def p_factor2(self, p):
        '''factor : NAME LP expr RP'''
        func_name = p[1]
        if func_name not in ExpressionHelper.func_map:
            raise Exception("Unknown function {}".format(func_name))
        if not callable(p[3]):
            raise Exception("Expression must be callable")
        param = copy(p[3])

        def f():
            return ExpressionHelper.func_map[func_name](param())
        p[0] = f

    def p_factor3(self, p):
        '''factor : LP expr RP'''
        p[0] = p[2]

    def p_factor4(self, p):
        '''factor : NAME LP params RP'''
        fname = p[1]
        if fname not in ExpressionHelper.func_map:
            raise Exception("Unknown function {}".format(fname))
        params = copy(p[3])

        def f():
            return ExpressionHelper.func_map[fname](*params)
        p[0] = f

    def p_params(self, p):
        '''params : params COMMA expr'''
        p[1].append(p[3])
        p[0] = p[1]

    def p_params1(self, p):
        '''params : expr'''
        p[0] = list([p[1]])

    def p_boolean_expression(self, p):
        '''boolean_expression : boolean_expression AND boolean_expression_unit
                              | boolean_expression OR boolean_expression_unit
                              | boolean_expression_unit'''
        if len(p) == 4:
            op = p[2]
            f1 = copy(p[1])
            f2 = copy(p[3])

            def bool_and(vs, cs):
                return f1(vs, cs) and f2(vs, cs)

            def bool_or(vs, cs):
                return f1(vs, cs) or f2(vs, cs)

            if op == '&':
                func = bool_and
            else:
                func = bool_or
            p[0] = func
        elif len(p) == 2:
            p[0] = p[1]
        if self._parsing_module:
            # the parser is parsing a module, since label must be defined outside of any module
            self._g = p[0]

    def p_boolean_expression_unit(self, p):
        '''boolean_expression_unit : NAME GT NUM
                                   | NAME LT NUM
                                   | NAME GE NUM
                                   | NAME LE NUM
                                   | NAME EQ NUM
                                   | NAME NEQ NUM'''
        n = copy(p[1])
        num = copy(p[3])
        bool_op = copy(p[2])

        def f(vs, cs):
            op1 = self._vcf_map[n]
            if callable(op1):
                op1 = op1()
            else:
                op1 = op1.get_value()
            op2 = num
            bool_func = self._gen_bool_func(bool_op)
            return bool_func(op1, op2)
        p[0] = f

    def p_boolean_expression_unit1(self, p):
        '''boolean_expression_unit : NAME GT expr
                                   | NAME LT expr
                                   | NAME GE expr
                                   | NAME LE expr
                                   | NAME EQ expr
                                   | NAME NEQ expr'''
        n = copy(p[1])
        expr = copy(p[3])
        op = copy(p[2])

        def f(vs, cs):
            if not callable(expr):
                raise Exception("expr in prismparser must be a function")
            op1 = self._vcf_map[n]
            if callable(op1):
                op1 = op1()
            else:
                op1 = op1.get_value()
            op2 = expr()
            bool_func = self._gen_bool_func(op)
            return bool_func(op1, op2)
        p[0] = f

    def p_boolean_expression_unit2(self, p):
        '''boolean_expression_unit : TRUE'''
        p[0] = lambda vs, cs: True

    def p_boolean_expression_unit3(self, p):
        '''boolean_expression_unit : FALSE'''
        p[0] = lambda vs, cs: False

    def p_formula_statement(self, p):
        '''formula_statement : FORMULA NAME ASSIGN expr SEMICOLON'''
        self._vcf_map[p[2]] = p[4]

    def p_label_statement(self, p):
        '''label_statement : LABEL NAME ASSIGN boolean_expression SEMICOLON'''
        ModelConstructor.get_model().add_label(p[2], p[4])

    def _resolve_literal(self, v, t):
        # v: value in string
        # t: type in string: int, double or bool
        if t not in self._type_map:
            raise Exception("Unrecognized type {}".format(t))
        return self._type_map[t](v)

    def _gen_bool_func(self, op):
        '''
        根据传入的op(str)返回相应的函数
        :param op: str
        :return: func
        '''
        eqfunc = lambda op1, op2: op1 == op2
        ltfunc = lambda op1, op2: op1 < op2
        lefunc = lambda op1, op2: ltfunc(op1, op2) or eqfunc(op1, op2)
        gtfunc = lambda op1, op2: not lefunc(op1, op2)
        nefunc = lambda op1, op2: not eqfunc(op1, op2)
        gefunc = lambda op1, op2: gtfunc(op1, op2) or eqfunc(op1, op2)
        map = {
            '<': ltfunc,
            '<=': lefunc,
            '>': gtfunc,
            '>=': gefunc,
            '==': eqfunc,
            '!=': nefunc
        }
        if op not in map:
            raise Exception("Unsupported boolean operation {}".format(op))
        return map[op]

    def parse_model(self, filepath):
        commentremoved = clear_comment(filepath)
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
        cur_dir = dirname(realpath(__file__))
        self.tokens = MyLexer.tokens
        self.parser = yacc.yacc(module=self, outputdir=cur_dir)


class ModelConstructor(object):
    _m = None

    def __init__(self, base_dir=None):
        self.parser = PRISMParser()
        self.parser.build()
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))
        self.logger.setLevel(logging.DEBUG)
        if base_dir:
            if not exists(base_dir) or not isdir(base_dir):
                return
            self._base_dir = base_dir

    @staticmethod
    def set_model(model):
        ModelConstructor._m = model

    @staticmethod
    def get_model():
        if ModelConstructor._m is None:
            raise Exception("Please specify a model type for the .prism file")
        return ModelConstructor._m

    def set_base_dir(self, base_dir):
        if not exists(base_dir) or not isdir(base_dir):
            return False
        self._base_dir = base_dir
        return True

    def _parse(self, filepath):
        self.parser.parse_model(filepath)
        return ModelConstructor.get_model()

    def parse(self, filename):
        '''
        解析.prism文件并返回
        :param filename: Die for example (extension excluded)
        :return: ModulesFile instance
        '''
        if not hasattr(self, "_base_dir"):
            self.logger.error("先设置模型所在路径")
            return
        path = join(self._base_dir, filename + ".prism")
        if not exists(path):
            self.logger.error("%s.prism 不存在", filename)
        return self._parse(path)


if __name__ == "__main__":
    modelConstructor = ModelConstructor()
    model = modelConstructor._parse("/Users/bitbook/Documents/SpacNN/prism_model/DPM.prism")


