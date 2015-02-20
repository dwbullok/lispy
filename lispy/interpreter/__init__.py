__author__ = 'Dan Bullok and Ben Lambeth'

from .scope import Scope
from ..common import ArgExpr
from .datatypes import StaticDatum, Symbol, FunctionCall, \
    ExprSeq, List
from .error import UnitNotFoundError


def make_datum(t):
    '''
    Create a Datum from a AstNode.

    :param t: the AST node convert from
    :type t: AstNode
    :return: A datum representing the node
    :rtype: datatypes.Datum
    '''
    if not isinstance(t,tuple):
        print(t)
    dtype, dval, dpos = t
    if dtype in ('BOOL', 'INT', 'FLOAT', 'STRING'):
        return StaticDatum(dpos, dval)
    elif dtype == 'ID':
        return Symbol(dpos, t)
    #elif dtype == 'SET':
    #    dval['value'] = make_datum(dval['value'])
    #    return Set(dpos, **dval)
    #elif dtype == 'DEFUN':
    #    dval['body'] = make_datum(dval['body'])
    #    return FunctionDef(dpos, **dval)
    elif dtype == 'LIST':
        dval = [make_datum(a) for a in dval]
        return List(dpos, dval)
    elif dtype == 'EXPRSEQ':
        return ExprSeq(dpos, [make_datum(i) for i in dval])
    else:
        raise Exception("Unknown statement type %s at %s.  Value = %s" % (
            dtype, dpos, dval))


__DEFAULT_BUILTINS__ = 'builtins'

from ..parser import Parser, Tokenizer
from .scope import GlobalScope
from ..builtins import global_builtins, interpreter_builtins


class Interpreter(object):
    def __init__(self, loader, debug_level=0, builtins=None):
        self._loader = loader
        self._tokenizer = Tokenizer()
        self._parser = Parser()
        self._global_scope = None

    def run_module(self, unit_name):
        source_text = self._loader.load_unit(unit_name)
        tokens = self._tokenizer.tokenize(unit_name, source_text)
        ast = self._parser.parse(tokens)
        self._global_scope = GlobalScope(global_builtins,
                                         interpreter_builtins,
                                         self)
        result=None
        for statement in ast:
            code = make_datum(statement)
            result = code.evaluate(self._global_scope)
        return result

    def evaluate_unit(self, unit_name):
        source_text = self._loader.load_unit(unit_name)
        tokens = self._tokenizer.tokenize(unit_name, source_text)
        ast = self._parser.parse(tokens)
        result=None
        for statement in ast:
            code = make_datum(statement)
            result = code.evaluate(self._global_scope)
        return result




