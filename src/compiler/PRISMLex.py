from ply.lex import lex
from removeComment import clear_comment

class MyLexer(object):
    def __init__(self, **kwargs):
        self.lexer = lex(object=self)

    keywords = {
        'dtmc': 'DTMC',
        'ctmc': 'CTMC',
        'const': 'CONST',
        'global': 'GLOBAL',
        'int' : 'INT',
        'double' : 'DOUBLE',
        'bool' : 'BOOL',
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
        'stdcdf': 'STDCDF',
        'formula': 'FORMULA'
    }


    tokens = [
                 'NAME',
                 'NUM',
                 'TYPE',
                 'MODELTYPE',
                 'OR', 'AND', 'NOT',
                 'EQ', 'NEQ', 'GE', 'LE', 'GT', 'LT',
                 'ASSIGN',
                 'ADD', 'MUL', 'DIV', 'MINUS',
                 'LP', 'RP', 'LB', 'RB',
                 "SEMICOLON",
                 "COLON",
                 "QUOTE",
                 "COMMA",
                 "THEN",  # -> in command statement
                 "NUMBERSIGN", # '#'
             ] + list(keywords.values())

    def t_NUM(self, t):
        r"[\-]?\d+\.?\d*"
        if t.value.find(r".") != -1:
            # float value type
            t.value = float(t.value)
        else:
            # integer type
            t.value = int(t.value)
        return t


    def t_NAME(self, t):
        r"[a-zA-Z_][0-9a-zA-Z_]*"
        t.type = self.keywords.get(t.value, 'NAME')
        return t


    def t_newline(self, t):
        r"\n+"
        t.lexer.lineno += len(t.value)


    t_ignore = ' \t'
    t_MODELTYPE = r"dtmc | ctmc"
    t_TYPE = 'int | double | bool'
    t_OR = r"\|"
    t_AND = r"&"
    t_NOT = r"!"
    t_EQ = r"=="
    t_NEQ = r"!="
    t_GE = r">="
    t_LE = r"<="
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
    t_THEN = r"\->"
    t_NUMBERSIGN = r"\#"

    def t_error(self, t):
        print "Illegal character '{}' ({}) in line {}.".format(t.value[0], hex(ord(t.value[0])), t.lexer.lineno)
        t.lexer.skip(1)

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
        self.tokenize_string(content)


def testPRISMLex():
    lexer = MyLexer()
    file_path = "../../prism_model/CommandTest.prism"
    removed_path = clear_comment(file_path)
    lexer.tokenize_file(removed_path)

if __name__ == "__main__":
    testPRISMLex()

