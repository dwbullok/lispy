__author__ = 'Dan Bullok and Ben Lambeth'


# builtin functions

# TODO: the user should be able to specify the set of builtins to load into
# an interpreter.

import operator


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
    return reduce(operator.sub, x[1:], x[0])


def timesBuiltin(parent_scope, *args):
    x = expandArgs(parent_scope, args)
    return reduce(operator.mul, x, 1)


def divBuiltin(parent_scope, *args):
    x = expandArgs(parent_scope, args)

    def sensitiveDiv(a, b):
        if type(a) is float or type(b) is float:
            return a / b
        else:
            return a // b

    return reduce(sensitiveDiv, x[1:], x[0])


def compareBuiltin(op):
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


def whileBuiltin(parent_scope, cond, body):
    last_value = None
    while (cond.evaluate(parent_scope)):
        last_value = body.evaluate(parent_scope)
    return last_value


def beginBuiltin(parent_scope, body):
    return body.evaluate(parent_scope)


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
    'if': ifBuiltin
}


