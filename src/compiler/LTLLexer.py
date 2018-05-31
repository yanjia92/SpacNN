from ply.lex import lex
from removeComment import clear_comment


class LTLLexer(object):
    def __init__(self):
        self.lexer = lex(object=self)


    keywords = {
        "true": "TRUE",
        "false": "FALSE",
        "U": "UNTIL",
        "X": "NEXT"
    }


    tokens = [
            "NAME",
            "AND",
            "OR",
            "NOT",
            "LT",
            "LE",
            "NUM"
    ] + list(keywords.values())


    t_ignore = " \t"
    t_UNTIL = r"U"
    t_NEXT = r"X"
    t_AND = r"&"
    t_OR = r"\|"
    t_NOT = r"!"
    t_LT = r"<"
    t_LE = r"<="


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


def testLTLLex():
    path = "../../prism_model/LTLTest.props"
    lexer = LTLLexer()
    lexer.tokenize_file(path)


if __name__ == "__main__":
    testLTLLex()




