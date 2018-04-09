import ply.yacc as yacc
import LexerTest
tokens = LexerTest.tokens

values = {}

def resolveexpr(op1, op2, symbol):
    m = {}
    m['+'] = lambda x,y : x+y
    m['-'] = lambda x,y : x-y
    m['*'] = lambda x,y : x*y
    m['/'] = lambda x,y : x/y
    return m[symbol](int(op1), int(op2))

def p_assign(p):
    '''assign : NAME EQUALS expr'''
    values[p[1]] = p[3]

def p_expr(p):
    '''expr : expr PLUS term
            | expr MINUS term'''
    p[0] = resolveexpr(p[1], p[3], p[2])

def p_expr_term(p):
    '''expr : term'''
    p[0] = p[1]

def p_term(p):
    '''term : term TIMES factor
            | term DIVIDE factor'''
    p[0] = resolveexpr(p[1], p[3], p[2])

def p_factor_term(p):
    '''term : factor'''
    p[0] = p[1]

def p_factor(p):
    '''factor : NUMBER'''
    p[0] = int(p[1])

yacc.yacc()

data = "x = 3 * 4 + 5 * 6"
yacc.parse(data)
print values


