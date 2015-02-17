__author__ = 'Dan Bullok and Ben Lambeth'

# builtin functions

# TODO: the user should be able to specify the set of builtins to load into
# an interpreter.

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


def whileBuiltin(parent_scope, cond, body):
    last_value = None
    while (cond.evaluate(parent_scope)):
        last_value = body.evaluate(parent_scope)
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


#: Default set of builtin functions (function name -> function)
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
    'while': whileBuiltin,
    'print': printBuiltin
}

interpreter_builtins = {
    'load': loadBuiltinMaker
}
