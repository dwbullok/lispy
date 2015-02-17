__author__ = 'Dan Bullok and Ben Lambeth'

import pprint

from ply import lex

from ..common import TokenPos, Syn, AstNode
from .error import UnclosedExpressionError, TooManyClosingParensError


P = pprint.PrettyPrinter(indent=4)

class TokenStack(object):
    '''
    A stack that Tokens and AstNodes can be pushed onto.  It tracks open and
    close parentheses.  use TokenStack.push(tok) to push individual tokens or
    expressions onto the stack.  If the token closes an open expression (is
    an RPAREN for which a matching LPAREN is on the stack), the push method
    will return a list representing every item (in order) between the LPAREN
    and the RPAREN.
    '''
    def __init__(self):
        self.reset()

    @property
    def is_empty(self):
        '''
        Is the stack empty?
        :return: True if the stack is empty, False otherwise
        :rtype: bool
        '''
        return len(self._stack)

    @property
    def top(self):
        '''
        :return: the top element of the stack
        :rtype: Syn, AstNode
        '''
        return self._stack[-1]

    def push(self, tok):
        '''
        Pushes a token onto the stack.  If tok is a RPAREN it should close an
        open expression (one started by an LPAREN). We find the  matching
        LPAREN and return everything between them.  The caller is responsible
        for processing the result and pushing it back onto the stack (possibly
        modified) if appropriate.

        If tok does not close an open expression, None is returned.

        :param tok: token or AstNode to push onto the stack.
        :type tok: Syn, AstNode
        :return: A list of elements enclosed between parentheses.  The left
                 and right parentheses are not returned.
        :rtype: list[Syn or AstNode], None
        '''
        # TODO: watch performance here and track lparen locations if necessary.

        if tok.type=='RPAREN':
            # pop until we find the opening LPAREN
            expr = self.pop_until_lparen()
            return expr
        self._stack.append(tok)
        if tok.type == 'LPAREN':
            self._lparens += 1
        return None

    def pop(self):
        if self.is_empty:
            raise ValueError("Attempt to pop from an empty stack.")
        if self.top.type == 'LPAREN':
            self._lparens -=1
        return self._stack.pop()

    def pop_until_lparen(self):
        result = []
        last_pos = None
        while (not self.is_empty):
            last_pos = self.top.pos
            if self.top.type == 'LPAREN':
                self.pop()
                return result
            # we build the list in reverse order so the expression list is
            # returned from left to right.
            result.insert(0, self.pop())
        raise TooManyClosingParensError(last_pos)

    def reset(self):
        '''
        Clear the contents of the stack and reset it to its initial state.
        '''
        self._lparens = 0
        self._stack = list()

    def pop_all(self):
        '''
        Retrieve the entire contents of the stack, in left to right order.
        This will clear the stack.
        If there are open expressions on the stack, we raise an
        UnclosedExpressionError

        :return: all the contents on the stackhc
        :rtype: list[Syn, AstNode]
        '''
        if self._lparens>0:
            # The stack contains unclosed expressions
            for e in reversed(self._stack):
                if e.type=='LPAREN':
                    raise UnclosedExpressionError(e.pos)
        result = self._stack
        self.reset()
        return result


class Parser(object):
    expr_types = {'BOOL', 'STRING', 'INT', 'FLOAT', 'ID', 'LIST', 'FUNC_CALL',
                  'SET', 'ID_LIST'}

    def __init__(self):
        pass

    def parse(self, tokens):
        '''
        Construct an AST from a list of tokens.

        :param tokens: the tokens to use as input to the parser
        :type tokens: list[Syn]
        :return: An abstract syntax tree representing the input
        :rtype: list[Ast]
        '''
        stack = TokenStack()
        for tok in tokens:
            expr = stack.push(tok)
            if expr is not None:
                stack.push(self.make_ast_node(expr))
        return stack.result()

    def make_ast_node(self, exprs):
        '''
        Convert a list of expressions (as returned from TokenStack.push )
        into an ast node.

        :param exprs: a list of expressions as returned from TokenStack.push
        :type expr: list[Syn or AstNode]
        :return: an ast node representing the expression list
        :rtype: AstNode
        '''


    def is_expr(self, item):
        '''
        Determine whether item is an expr.

        :param item: an item
        :type item: Syn, AstNode
        :return: True if item is an expr, False otherwise.
        :rtype: bool
        '''
        return item.type in self.expr_types

    def is_func_call(self, expr):
        '''
        Determine whether expr is a function call

        :param expr: an expression
        :type expr: Syn, AstNode
        :return: True if item is an expr, False otherwise.
        :rtype: bool
        '''
        if expr.type != 'LIST':
            return False
        name = expr.value[0]
        args = expr.value[1:]
        if not self.is_id(name):
            return False
        return AstNode('FUNC_CALL',
                       {'name': name, 'arg_exprs': args},
                       name.pos)

    def is_id(self, expr):
        '''
        Determine whether expr is an ID

        :param expr: an expression
        :type expr: Syn, AstNode
        :return: True if expr is an ID, False otherwise.
        :rtype: bool
        '''
        # TODO: if it is possible for the evaluation of an expression to
        #       yield an ID, we need to handle that here.
        return expr.type=='ID'

    def is_id_list(self, expr):
        '''
        Determine whether expr is a list of IDs

        :param expr: an expression
        :type expr: AstNode
        :return: True if expr is a list of IDs, False otherwise.
        :rtype: bool
        '''
        if expr.type == 'LIST':
            for e in expr:
                if not self.is_id(expr):
                    return False
            return True
        return False

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

