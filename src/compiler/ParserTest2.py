# -*- coding: utf-8 -*-
# 一个带函数调用的expression的parser
import ply.yacc as yacc
import LexerTest
tokens = LexerTest.tokens
from math import *

func_map = {}
supported_func = [log]
for func in supported_func:
    func_map[func.__name__] = func


variables = {
    "a" : 1,
    "b" : 2
}

constants = {
    "c1" : 3,
    "c2" : 4
}

binary_op_map = {
    '+' : lambda x,y : x + y,
    '-' : lambda x,y : x - y,
    '*' : lambda x,y : x * y,
    '/' : lambda x,y : x / y
}


def p_expression(p):
    '''expression : expression PLUS term
                  | expression MINUS term'''
    func = binary_op_map[p[2]]
    p[0] = func(p[1], p[3])


def p_expression1(p):
    '''expression : NAME LP expression RP'''
    p[0] = resolve_func_expr(p[1], p[3])


def p_expression2(p):
    '''expression : term'''
    p[0] = p[1]


def p_term(p):
    '''term : term TIMES factor
            | term DIVIDE factor'''
    func = binary_op_map[p[2]]
    p[0] = func(p[1], p[3])


def p_term1(p):
    '''term : factor'''
    p[0] = p[1]

def p_factor(p):
    '''factor : NUMBER'''
    p[0] = p[1]


def p_factor1(p):
    '''factor : NAME LP expression RP'''
    p[0] = resolve_func_expr(p[1], p[3])


def p_factor2(p):
    '''factor : NAME'''
    value = variables.get(p[1], None)
    if not value:
        value = constants.get(p[1])
    p[0] = value


def resolve_func_expr(func_name, *value):
    func = func_map.get(func_name, None)
    if not func:
        raise Exception("not supported func {}".format(func_name))
    return func(*value)


yacc.yacc()

data = "log(a+b)"
print yacc.parse(data) == log(variables['a'] + variables['b'])







