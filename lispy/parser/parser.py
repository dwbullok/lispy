__author__ = 'Dan Bullok and Ben Lambeth'

import pprint

from ply import lex, yacc

from ..common import TokenPos, Syn


P = pprint.PrettyPrinter(indent=4)


class LineTracker(object):
    """Tracks line numbers and computes TokenPos tuples.  This only works if
    we ask for the token positions in the order they occur (this doesn't
    handle random access of token positions).
    """

    def __init__(self, unit_name):
        self._unit_name = unit_name
        self._last_line_offset = 0
        self._line = 0


    def inc_line(self, char_offset):
        """
        Records a newline.  This increments the line counter and records the
        character offset where the newline occurs.

        :param char_offset: the character offset (within the unit) of the
                            newline.
        :type char_offset: int
        """
        self._last_line_offset = char_offset
        self._line += 1

    def get_pos(self, char_offset):
        """
        Calculate a TokenPos for a given character offset within the unit.

        Note that we only support looking up the positions of tokens that
        occur AFTER the last newline we've tracked.

        :param char_offset: the character offset (within the unit) of a token
        :type char_offset: int

        :return: A TokenPos that indicates the position within the unit of
                 the given character offset.
        :rtype: TokenPos
        """

        assert (char_offset >= self._last_line_offset)
        return TokenPos(self._unit_name,
                        self._last_line_offset + 1,
                        char_offset - self._last_line_offset + 1)


class LispyParser(object):
    '''
    Parser for LisPy code.
    '''
    def __init__(self, lex_kwargs=None, yacc_kwargs=None):
        '''
        :param lex_kwargs: kwargs to pass to lex
        :type lex_kwargs: dict
        :param yacc_kwargs: kwargs to pass to yacc
        :type yacc_kwargs: dict
        '''
        lex_kwargs = lex_kwargs if lex_kwargs else dict()
        yacc_kwargs = yacc_kwargs if yacc_kwargs else dict()
        self._lexer = lex.lex(module=self, **lex_kwargs)
        self._parser = yacc.yacc(module=self, **yacc_kwargs)
        self._files = dict()

    def parse(self, unit_name, input_text):
        '''
        Parse input_text.

        :param unit_name: the name of the translation unit (used to record
                          position information).
        :type unit_name: str
        :param input_text: the source text to parse
        :type input_text: str
        :return: abstract syntax tree
        :rtchype: Syn
        '''
        self._tracker = LineTracker(unit_name)
        result = self._parser.parse(input_text, lexer=self._lexer)
        self._files[unit_name] = result
        return result

    def get_syn(self, tok, s_type, s_value):
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
        'LPAREN',
        'RPAREN',
        'DEFUN',
        'SET',
        'ID',
        'SQUOTE',
        'COMMENT'
    )

    r_id_initial = ''
    r_id_subsequent = '[a-zA-Z_!$%^*/:<=>?~^]'

    # begin lexer tokens

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
        t.value = self.get_syn(t, 'STRING', t.value[1:-1])
        return t


    def t_BOOL(self, t):
        r'\#[tf]'
        t.value = self.get_syn(t, 'BOOL', (t.value == '#t'))
        return t


    def t_FLOAT(self, t):
        r'-?[0-9]+\.[0-9]*([eE](-?[0-9]+))?'
        t.value = self.get_syn(t, 'FLOAT', float(t.value))
        return t


    def t_INT(self, t):
        r'-?[0-9]+'
        t.value = self.get_syn(t, 'INT', int(t.value))
        return t


    t_LPAREN = r'\('
    t_RPAREN = r'\)'


    def t_ID(self, t):
        r'[-+]|([a-zA-Z_!$%*/:<=>?~^][a-zA-Z_!$%^*/:<=>?~0-9.+\-^]*)'
        # check for special keywords
        if (t.value == 'defun'):
            t.type = 'DEFUN'
            t.value = self.get_syn(t, 'DEFUN', t.value)
        elif (t.value == 'set'):
            t.type = 'SET'
            t.value = self.get_syn(t, 'SET', t.value)
        else:
            t.value = self.get_syn(t, 'ID', t.value)
        return t


    t_SQUOTE = r"'"

    def t_COMMENT(self, t):
        r';[^\n]'
        pass


    # end lexer tokens


    # begin grammar



    # TODO: yacc will complain about unused tokens.  Filter them out to avoid
    # warnings

    # TODO: implement dictionaries
    # TODO: handle SQUOTE

    # TODO: simplify the parser by removing special rules for set and defun -
    # We can handle these as instances of a list.
    # We check in p_list for the case when the first elem of the list is
    # set or defun.  Then verify that the rest of the list matches
    #       expected signature.  If not, it's a syntax error.
    #       This should resolve the shift/reduce conflict warnings

    def p_error(self, p):
        print("Syntax error at token", p.type)
        raise SyntaxError

    def p_expr(self, p):
        '''expr : atom
                | defun
                | set
                | func_call
                | list
        '''
        p[0] = p[1]


    def p_func_call(self, p):
        '''func_call : LPAREN ID exprseq RPAREN
        '''
        p[0] = Syn('FUNC_CALL', {'name': p[2], 'arg_exprs': p[3]}, p[2].pos)


    def p_ids(self, p):
        '''ids : ID
               | ID ids
        '''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]


    def p_atom(self, p):
        '''atom : BOOL
                | STRING
                | INT
                | FLOAT
                | ID
        '''
        p[0] = p[1]


    def p_exprseq(self, p):
        '''exprseq : expr
                   | expr exprseq
        '''
        if len(p) == 2:
            p[0] = Syn('EXPRSEQ', [p[1]], p[1].pos)
        else:
            p[0] = Syn('EXPRSEQ', [p[1]] + p[2].value, p[1].pos)


    def p_list(self, p):
        '''list : LPAREN exprseq RPAREN
                | LPAREN RPAREN
        '''
        if len(p) == 3:
            p[0] = Syn('LIST', list(), p[1].pos)
        else:
            p[0] = Syn('LIST', p[2].value, p[2].pos)


    def p_defun(self, p):
        '''defun : LPAREN DEFUN ID LPAREN ids RPAREN exprseq RPAREN
        '''
        p[0] = Syn('DEFUN', {'name': p[3], 'args': p[5], 'body': p[7]},
                   p[2].pos)


    def p_set(self, p):
        '''set : LPAREN SET ID expr RPAREN
        '''
        p[0] = Syn('SET', {'name': p[3], 'value': p[4]}, p[2].pos)

        # end grammar

