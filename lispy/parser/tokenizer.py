__author__ = 'Dan Bullok and Ben Lambeth'

import pprint

from ply import lex

from ..common import TokenPos, Syn

from .linetracker import LineTracker

class Tokenizer(object):
    '''
    Parser for LisPy code.
    '''
    def __init__(self, lex_kwargs=None):
        '''
        :param lex_kwargs: kwargs to pass to lex
        :type lex_kwargs: dict
        '''
        lex_kwargs = lex_kwargs if lex_kwargs else dict()
        self._lexer = lex.lex(module=self, **lex_kwargs)
        self._ignore_tokens = {'COMMENT'}

    def tokenize(self, unit_name, input_text):
        '''
        Tokenize input_text.

        :param unit_name: the name of the translation unit (used to record
                          position information - this class does *not* load
                          the translation unit).
        :type unit_name: str
        :param input_text: the source text to parse
        :type input_text: str
        :return: tokens
        :rtype: list[Syn]
        '''
        self._tracker = LineTracker(unit_name)
        self._lexer.input(input_text)
        result = []
        while True:
            tok = self._lexer.token()
            if tok is None:
                break
            if tok.type not in self._ignore_tokens:
                result.append(tok.value)
        return result


    def _make_token(self, tok, s_type, s_value):
        '''
        Create a Syn from a token.  Determines the current TokenPos.

        :param tok: token
        :type tok: LexToken
        :param s_type: type of the token
        :type s_type: str
        :param s_value: value of the token
        :type s_value: varies
        :return: A Syn containing the token and its position
        :rtype: Syn
        '''
        return Syn(s_type, s_value, self._tracker.get_pos(self._lexer.lexpos))

    tokens = (
        'STRING',
        'BOOL',
        'FLOAT',
        'INT',
        'PAREN',
        'ID',
        'SQUOTE',
        'COMMENT',
        'KEYWORD'
    )

    # begin lexer tokens

    def t_keyword(self, t):
        r'&[-a-zA-Z_]'
        t.value = self._make_token(t, 'KEYWORD', t.value)
        return t

    def t_newline(self, t):
        r'\n+'
        # this is a bit awkward - we have to send individual newlines to the
        # tracker.  This should handle a regex that matches more than just
        # newlines  (not sure if that will ever be necessary).
        char_idx = self._lexer.lexpos
        for n in t.value:
            if n == '\n':
                self._tracker.inc_line(char_idx)
            char_idx += 1
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    t_ignore = " \t"

    def t_STRING(self, t):
        r'"([^"]|(\\")|\\)*"'
        t.value = self._make_token(t, 'STRING', t.value[1:-1])
        return t

    def t_BOOL(self, t):
        r'\#[tf]'
        t.value = self._make_token(t, 'BOOL', (t.value == '#t'))
        return t

    def t_FLOAT(self, t):
        r'-?[0-9]+\.[0-9]*([eE](-?[0-9]+))?'
        t.value = self._make_token(t, 'FLOAT', float(t.value))
        return t

    def t_INT(self, t):
        r'-?[0-9]+'
        t.value = self._make_token(t, 'INT', int(t.value))
        return t

    def t_PAREN(self, t):
        r'[()]'
        print('t=%s'%str(t))
        if t.value == '(':
            t.value = self._make_token(t, 'LPAREN', '(')
        elif t.value == ')':
            t.value = self._make_token(t, 'RPAREN', ')')
        return t

    def t_ID(self, t):
        r'[-+]|([a-zA-Z_!$%*/:<=>?~^][a-zA-Z_!$%^*/:<=>?~0-9.+\-^]*)'
        t.value = self._make_token(t, 'ID', t.value)
        return t

    def t_SQUOTE(self, t):
        r"'"
        t.value = self._make_token(t, 'SQUOTE', t.value)
        return t

    def t_IQUOTE(self, t):
        r'[!]'
        t.value = self._make_token(t, 'IQUOTE', t.value)
        return t

    def t_COMMENT(self, t):
        r';[^\n]'
        t.value = self._make_token(t, 'COMMENT', t.value)
        return t

