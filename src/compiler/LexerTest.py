import ply.lex as lex

reserved_keywords = {
    'stdcdf' : 'STDCDF'
}

tokens = [
    'NAME',
    'NUMBER',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'EQUALS',
    'LP', 'RP'
] + reserved_keywords.values()

t_ignore = ' \t'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r"/"
t_EQUALS = r'='
t_LP = r'\('
t_RP = r"\)"

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved_keywords.get(t.value, "NAME")
    return t


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

lex.lex()