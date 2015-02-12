__author__ = 'Dan Bullok and Ben Lambeth'

import pprint

P = pprint.PrettyPrinter(indent=4)

tokens = (
    'STRING',
    'BOOL',
    'FLOAT',
    'INT',
    'LPAREN',
    'RPAREN',
    'DEFUN',
    'SET',
    'ID',
    'SQUOTE',
    'LINE_COMMENT'
)

r_id_initial = ''
r_id_subsequent = '[a-zA-Z_!$%^*/:<=>?~^]'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


t_ignore = " \t"


# Build the lexer import ply.lex as lex lex.lex()

def t_STRING(t):
    r'"([^"]|(\\")|\\)*"'
    t.value = ('STRING', t.value[1:-1])
    return t


def t_BOOL(t):
    r'\#[tf]'
    t.value = ('BOOL', (t.value == '#t'))
    return t


def t_FLOAT(t):
    r'-?[0-9]+\.[0-9]*([eE](-?[0-9]+))?'
    t.value = ('FLOAT', float(t.value))
    return t


def t_INT(t):
    r'-?[0-9]+'
    t.value = ('INT', int(t.value))
    return t


t_LPAREN = r'\('
t_RPAREN = r'\)'


def t_ID(t):
    r'[-+]|([a-zA-Z_!$%*/:<=>?~^][a-zA-Z_!$%^*/:<=>?~0-9.+\-^]*)'
    if (t.value == 'defun'):
        t.type = 'DEFUN'
        t.value = ('DEFUN', t.value)
    elif (t.value == 'set'):
        t.type = 'SET'
        t.value = ('SET', t.value)
    else:
        t.value = ('ID', t.value)
    return t


t_SQUOTE = r"'"
t_LINE_COMMENT = r';[^\n]'

from ply import lex, yacc

lexer = lex.lex()


def p_expr(p):
    '''expr : atom
            | defun
            | set
            | func_call
            | list
    '''
    p[0] = p[1]


def p_func_call(p):
    '''func_call : LPAREN ID exprseq RPAREN
    '''
    p[0] = ('FUNC_CALL', {'name': p[2], 'arg_exprs': p[3]})


def p_ids(p):
    '''ids : ID
           | ID ids
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[2]


def p_atom(p):
    '''atom : BOOL
            | STRING
            | INT
            | FLOAT
            | ID
    '''
    p[0] = p[1]


def p_exprseq(p):
    '''exprseq : expr
               | expr exprseq
    '''
    if len(p) == 2:
        p[0] = ('EXPRSEQ', [p[1]])
    else:
        p[0] = ('EXPRSEQ', [p[1]] + p[2][1])


def p_list(p):
    '''list : LPAREN exprseq RPAREN
            | LPAREN RPAREN
    '''
    if len(p) == 3:
        p[0] = ('LIST', list())
    else:
        p[0] = ('LIST', p[2][1])


def p_defun(p):
    '''defun : LPAREN DEFUN ID LPAREN ids RPAREN exprseq RPAREN
    '''
    p[0] = ('DEFUN', {'name': p[3], 'args': p[5], 'body': p[7]})


def p_set(p):
    '''set : LPAREN SET ID expr RPAREN
    '''
    p[0] = ('SET', {'name': p[3], 'value': p[4]})


parser = yacc.yacc(debug=True)

test = """( ( + 1 2)
            ( + 1 2) )"""

# test = """(1 3 4)"""

test = """((defun f (x) (+ x 2))
          (f 8))"""
test = """( #t
  #f)"""

test = """(
          (defun f (x)
            (defun g (y) (+ x y 4.0))
            (+ (g 5) x 1)
          )
          ("homer" (f 2))
          (if (= 2 (f 3)) 6.7 "bart")
          (set x 2)
        )
"""

"""while True:
    tok = lexer.token()
    if not tok: break
    print(tok)
"""

from scope import make_datum, GlobalScope, global_builtins
import logging

log = logging.getLogger()

tree = parser.parse(test, debug=log)
P.pprint(tree)
code = make_datum(tree)
global_scope = GlobalScope(global_builtins)

print(code)
print(code.evaluate(global_scope))
