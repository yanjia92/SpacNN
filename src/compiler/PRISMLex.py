import ply.lex as lex

class MyLexer(object):
    keywords = {
        'dtmc': 'DTMC',
        'ctmc': 'CTMC',
        'const': 'CONST',
        'global': 'GLOBAL',
        'int': 'INT',
        'double': 'DOUBLE',
        'bool': 'BOOL',
        'label': 'LABEL',
        'module': 'MODULE',
        'endmodule': 'ENDMODULE',
        'init': 'INIT',
        'true': 'TRUE',
        'false': 'FALSE',
        'max': 'MAX',
        'min': 'MIN',
        'exp': 'EXP',
        'log': 'LOG',
        'pow': 'POW',
        'stdcdf': 'STDCDF'
    }

    tokens = [
                 'NAME',
                 'NUM',
                 'MODELTYPE',
                 'OR', 'AND',
                 'EQ', 'NEQ', 'GTEQ', 'LTEQ', 'GT', 'LT',
                 'ASSIGN',
                 'ADD', 'MUL', 'DIV', 'MINUS',
                 'LP', 'RP', 'LB', 'RB',
                 "SEMICOLON",
                 "COLON",
                 "QUOTE",
                 "COMMA"
             ] + list(keywords.values())


    def t_NAME(self, t):
        r"[a-zA-Z_][0-9a-zA-Z_]*"
        t.type = self.keywords.get(t.value, 'NAME')
        return t


    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)


    t_ignore = ' \t'
    t_NUM = r"[\+\-]?\d+\.?\d*"
    t_MODELTYPE = r"dtmc | ctmc"
    t_OR = r"\|"
    t_AND = r"&"
    t_EQ = r"=="
    t_NEQ = r"!="
    t_GTEQ = r">="
    t_LTEQ = r"<="
    t_GT = r">"
    t_LT = r"<"
    t_ASSIGN = r"="
    t_ADD = r"\+"
    t_MINUS = r"\-"
    t_MUL = r"\*"
    t_DIV = r"/"
    t_LP = r"\("
    t_RP = r"\)"
    t_LB = r"\["
    t_RB = r"\]"
    t_SEMICOLON = r";"
    t_COLON = r":"
    t_QUOTE = r"'"
    t_COMMA = r","

    def t_error(self, t):
        print "Illegal character '{}' ({}) in line {}.".format(t.value[0], hex(ord(t.value[0])), t.lexer.lineno)
        t.lexer.skip(1)

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def tokenize_string(self, code):
        self.lexer.input(code)
        for token in self.lexer:
            print(token.type, token.value)

    def tokenize_file(self, _file):
        if type(_file) == str:
            _file = open(_file)
        content = ''
        for line in _file:
            content += line
        return self.tokenize_string(content)


def testPRISMLex():
    lexer = MyLexer()
    lexer.build()
    lexer.tokenize_file("./smalltest.prism")

if __name__ == "__main__":
    testPRISMLex()

