'''
    Builtin functions for the interpreter.
'''

__author__ = 'Dan Bullok and Ben Lambeth'

# TODO: the user should be able to specify the set of builtins to load into
# an interpreter.


from ..interpreter.error import LispySyntaxError,ArgCountError
import operator, functools


def ifBuiltin(parent_scope, condition, true_expr, false_expr):
    if condition.evaluate(parent_scope):
        return true_expr.evaluate(parent_scope)
    else:
        return false_expr.evaluate(parent_scope)


def expandArgs(parent_scope, args):
    return [a.evaluate(parent_scope) for a in args]


def plusBuiltin(parent_scope, *args):
    x = expandArgs(parent_scope, args)
    return sum(x)


def minusBuiltin(parent_scope, *args):
    x = expandArgs(parent_scope, args)
    return functools.reduce(operator.sub, x[1:], x[0])


def timesBuiltin(parent_scope, *args):
    x = expandArgs(parent_scope, args)
    return functools.reduce(operator.mul, x, 1)


def divBuiltin(parent_scope, *args):
    x = expandArgs(parent_scope, args)

    def sensitiveDiv(a, b):
        if type(a) is float or type(b) is float:
            return a / b
        else:
            return a // b

    return functools.reduce(sensitiveDiv, x[1:], x[0])


def compareBuiltin(op):
    '''
    Create a comparison operator function.

    :param op: operator function to use for comparison
    :type op: (any, any) -> bool
    :return: comparison function suitable for use as a builtin

    '''
    def f(parent_scope, *args):
        last_value = args[0].evaluate(parent_scope)
        for a in args[1:]:
            v = a.evaluate(parent_scope)
            if op(v, last_value):
                last_value = v
                continue
            return False
        return True
    return f


eqBuiltin = compareBuiltin(lambda x, y: x == y)
neqBuiltin = compareBuiltin(lambda x, y: x != y)
ltBuiltin = compareBuiltin(lambda x, y: x < y)
gtBuiltin = compareBuiltin(lambda x, y: x > y)
gteBuiltin = compareBuiltin(lambda x, y: x >= y)
lteBuiltin = compareBuiltin(lambda x, y: x <= y)
orBuiltin = compareBuiltin(lambda x, y: x or y)
andBuiltin = compareBuiltin(lambda x, y: x and y)


def whileBuiltin(parent_scope, cond, *body):
    last_value = None
    while (cond.evaluate(parent_scope)):
        for a in body:
            last_value = a.evaluate(parent_scope)
    return last_value


def beginBuiltin(parent_scope, *body):
    last_value = None
    for a in body:
        last_value = a.evaluate(parent_scope)
    return last_value

def printBuiltin(parent_scope, *args):
    last_value = None
    for a in args:
        last_value = a.evaluate(parent_scope)
        print(last_value)
    return last_value

def loadBuiltinMaker(interpreter):
    def loadBuiltin(parent_scope, *unit_names):
        assert (len(unit_names)>=1)
        result=None
        for unit in unit_names:
            result = interpreter.evaluate_unit(unit)
        return result
    return loadBuiltin

def optional_keyword(*args):
    arg_dict = {}
    for a in args:
        if a.type == 'ID':
            arg_dict[a.value] = None
        elif a.type == 'LIST':
            if len(a.value) != 2:
                raise LispySyntaxError(a.pos,
                                       "Default argument must be defined as "
                                       "a list of length 2.")
            name, def_val = a.value
            arg_dict[name] = def_val
    return arg_dict

def rest_keyword(args):
    if len(args)>1:
        raise LispySyntaxError(args[0].pos,
                               "&rest keyword only allows one id.")
    arg_name = args[0]
    arg_dict = {arg_name: []}
    return arg_dict

from ..interpreter.datatypes import Quote

def key_keyword(*args):
    return optional_keyword(*args)

def quoteBuiltin(parent_scope, arg):
    return Quote(arg.pos, arg)


def listBuiltin(parent_scope, *args):
    return [a.evaluate(parent_scope) for a in args]

def defunBuiltin(parent_scope, name, args, body):
    f = FunctionDef(args, body)
    setBuiltin(parent_scope, name, f)
    return f

def setBuiltin(parent_scope, expr, value):
    name = expr.evaluate(parent_scope)
    v = value.evaluate(parent_scope)
    parent_scope.assign(name, v)
    return v

def setqBuiltin(parent_scope, name, value):
    expr = quoteBuiltin(parent_scope, name)
    return setBuiltin(expr,value)


def split_arg_list(arg_list, interpreter_keywords):
    result = {k: list() for k in interpreter_keywords}
    result['positional'] = list()
    current = 'positional'
    idx = 0
    for a in arg_list:
        if a.type=='KEYWORD':
            current = a.value
            result[current] = list()
        else:
            result[current].append((idx, a))
            idx += 1
    return result

from ..common import ArgExpr

class FunctionDef(object):
    '''
    A function definition.
    '''

    def __init__(self, args, body,
                 interpreter_keywords=None,
                 safe_arg_keywords=None):
        '''
        :param args: the arguments this function takes
        :type args: a list of identifier tokens
        :param body: the body of the function
        :type body: ExprSeq
        '''
        # if safe_arg_keywords is None:
        #     safe_arg_keywords = set()
        #
        # if interpreter_keywords is None:
        #     interpreter_keywords = dict()
        #
        # keywords = tuple(a.value for a in args if a.type == 'KEYWORD')
        # if len(keywords) > 0:
        #     if keywords not in safe_arg_keywords:
        #         raise SyntaxError("Illegal keyword sequence: %s" % str(
        #             keywords))
        #     arg_groups = split_arg_list(args, interpreter_keywords)
        #     positional_args = arg_groups.pop('positional')
        #     for (kw, v) in arg_groups.items():
        #         interpreter_keywords[kw](*v)

        positional_args = []
        optional_args = []
        rest_arg = None
        key_args = []

        self._args = [a for a in args]
        self._body = body

    def __call__(self, parent_scope, *arg_vals):
        if (len(self._args) != len(arg_vals)):
            raise ArgCountError("Argument count mismatch.  Expected %d args "
                                "but received %d."%(len(self._args),
                                                    len(arg_vals)))
        scope = parent_scope.make_child_scope()
        for (id, val) in zip(self._args, arg_vals):
            # we store the values of the args - they might not actually be
            # computed.  This allows lazy evaluation of function args
            scope.create_local(id, ArgExpr(parent_scope, val))
        return self._body.evaluate(scope)
        # last_value = None
        # for item in self._body:
        # last_value = item.evaluate(scope)
        # return last_value

#: Default set of builtin functions

global_builtins = {
    '+': plusBuiltin,
    '-': minusBuiltin,
    '*': timesBuiltin,
    '/': divBuiltin,
    '=': eqBuiltin,
    '!=': neqBuiltin,
    '<': ltBuiltin,
    '>': gtBuiltin,
    '<=': lteBuiltin,
    '>=': gteBuiltin,
    'or': orBuiltin,
    'and': andBuiltin,
    'if': ifBuiltin,
    'begin': beginBuiltin,
    'set': setBuiltin,
    'setq': setqBuiltin,
    'while': whileBuiltin,
    'print': printBuiltin,
    'quote': quoteBuiltin,
    'defun': defunBuiltin,
    'list': listBuiltin
}


#: Default set of interpreter builtins

interpreter_builtins =  {
    'load': loadBuiltinMaker
}

interpreter_keywords = {
    '&optional': optional_keyword,
    '&rest': rest_keyword,
    '&key': key_keyword,
}

safe_arg_keywords = {('&optional','&rest'),
                     ('&rest',),
                     ('&optional',),
                     ('&key',)}
