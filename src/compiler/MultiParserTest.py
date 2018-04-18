import ply.yacc as yacc
from PRISMLex import MyLexer

class AddExprParser(object):
    def __init__(self, lexer=None):
        self.parser = None
        self.tokens = MyLexer.tokens
        self.parser = yacc.yacc(module=self)
        self.lexer = lexer

    def p_add_expr(self, p):
        '''expr : expr ADD NUM'''
        p[0] = p[1] + p[3]

    def p_expr(self, p):
        '''expr : NUM'''
        p[0] = p[1]

    def parseString(self, data):
        return self.parser.parse(data, self.lexer)


class AddMinusExprParser(AddExprParser):
    def __init__(self, lexer=None):
        AddExprParser.__init__(self, lexer)

    def p_minus_expr(self, p):
        '''expr : expr MINUS NUM'''
        p[0] = p[1] - p[3]


def test():
    data1 = "1 + 2"
    data2 = "3 - 1"
    parser = AddMinusExprParser(MyLexer().lexer)
    print parser.parseString(data1)
    print parser.parseString(data2)


if __name__ == "__main__":
    test()