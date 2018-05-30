from ply.lex import lex
from removeComment import clear_comment


class LTLLexer(object):
    def __init__(self):
        self.lexer = lex(object=self)

