# -*- coding:utf-8 -*-
import ply.yacc as yacc
from PRISMLex import MyLexer
import copy

tokens = MyLexer.tokens


_vars = {
    'a' : 1,
    'b' : 2,
}

def p_bool_expr(p):
    '''bool_expr : bool_expr AND bool_expr_unit'''
    def f():
        result = p[1]() and p[3]()
        return result
    p[0] = f


def p_bool_expr2(p):
    '''bool_expr : bool_expr OR bool_expr_unit'''
    def f():
        result = p[1]() or p[3]()
        return result
    p[0] = f


def p_bool_expr3(p):
    '''bool_expr : bool_expr_unit'''
    p[0] = p[1]


def p_bool_expr_unit(p):
    '''bool_expr_unit : NAME EQ NUM
                      | NAME NEQ NUM
                      | NAME GT NUM
                      | NAME LT NUM
                      | NAME GE NUM
                      | NAME LE NUM'''
    # 将每一个bool_expr_unit编译成一个函数对象
    slices_cpy = copy.copy(p.slice)
    def f():
        return resolve_bool_expr(slices_cpy[1].value, slices_cpy[3].value, slices_cpy[2].value)
    p[0] = f


def resolve_bool_expr(val1, val2, op):
        # val1 val2分别为两个用于比较的数
        # op为比较操作符
        var = _vars[val1]
        if '<' == op:
            return var < val2
        if '>' == op:
            return var > val2
        if '>=' == op :
            return var >= val2
        if '<=' == op:
            return var <= val2
        if '==' == op:
            return var == val2
        if '!=' == op:
            return var != val2


yacc.yacc()
# b = 2 a = 1
data = "b != 2 | a == 0"
myLexer = MyLexer()
lexer = myLexer.lexer
result = yacc.parse(data, lexer=lexer)
print result()
_vars['a'] = 0
print result()



