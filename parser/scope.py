__author__ = 'Dan Bullok and Ben Lambeth'
from collections import namedtuple
ArgExpr = namedtuple('ArgExpr', 'parent_scope expr')

class Scope(object):
    def __init__(self,parent=None):
        self._defns = dict()
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    def get(self, id):
        '''
        Retrieve the definition of an identifier.  Look in the local scope,
        then ancestor scopes.
        :param id: identifier to look up.
        :type id: str
        :return: the definition of the given identifier
        :rtype: Definition
        '''
        defn = None
        try:
            if self._parent is None:
                defn = self._defns[id]
            else:
                defn =  self._defns.get(id, self._parent.get(id))
        except KeyError as e:
            return None
        if isinstance(defn, ArgExpr):
            # handle lazy arg evaluation
            return defn.expr.evaluate(defn.parent_scope)
        else:
            return defn


    def assign(self, id, defn):
        '''
        :param id:
        :type id:
        :param defn:
        :type defn:
        :return:
        :rtype:
        '''
        if self.get(id) is None:
            # id has not yet been defined: it goes in the local scope
            self._defns[id] = defn
        elif id in self._defns:
            # id has been defined in this scope.  We update it
            self._defns[id] = defn
        else:
            # id has been defined in a parent.
            self._parent.assign(id, defn)

    def create_local(self, id, defn):
        if id in self._defns:
            raise Exception("Can't create a variable that has already been defined: %s"%id)
        self._defns[id] = defn




class Datum(object):
    def evaluate(self, parent_scope):
        pass
    @property
    def value(self):
        return self


class StaticDatum(Datum):
    def __init__(self, value):
        self._value = value

    def evaluate(self, parent_scope):
        return self._value

    @property
    def value(self):
        return self._value

    def __str__(self):
        return str(self._value)


class FunctionDef(Datum):
    def __init__(self, name, args, body):
        self._name = name[1]
        self._args = [a[1] for a in args]
        self._body = body

    def __call__(self, parent_scope, *arg_vals):
        assert (len(self._args) == len(arg_vals))
        scope = Scope(parent_scope)
        for (id, val) in zip(self._args, arg_vals):
            # we store the values of the args - they might not actually be
            # computed.  This allows lazy evaluation of function args
            scope.create_local(id, ArgExpr(parent_scope, val))
        return self._body.evaluate(scope)
        #last_value = None
        #for item in self._body:
        #    last_value = item.evaluate(scope)
        #return last_value

    def evaluate(self, parent_scope):
        parent_scope.assign(self._name, self)

class ExprSeq(Datum):
    def __init__(self, items):
        self._items = items

    def evaluate(self, parent_scope):
        scope = Scope(parent_scope)
        last_value = None
        for e in self._items:
            last_value = e.evaluate(scope)
        return last_value

    @property
    def value(self):
        return [i.value for i in self._items]


class List(ExprSeq):
    def evaluate(self, parent_scope):
        return  [i.evaluate(parent_scope) for i in self._items]


class FunctionCall(Datum):
    def __init__(self, name, arg_exprs):
        self._name = name[1]
        self._arg_exprs = arg_exprs

    def evaluate(self, parent_scope):
        func_def = parent_scope.get(self._name)
        if func_def is None:
            raise Exception("Undefined function '%s'" % str( self._name))

        return func_def(parent_scope, *self._arg_exprs)


class Set(Datum):
    def __init__(self, name, value):
        self._name = name[1]
        self._value = value

    def evaluate(self, parent_scope):
        v = self._value.evaluate(parent_scope)
        parent_scope.assign(self._name, v)
        return v


class VarRef(Datum):
    def __init__(self, name):
        self._name = name
    def evaluate(self, parent_scope):
        return parent_scope.get(self._name)

def ifBuiltin(parent_scope, condition, true_expr, false_expr):
    if condition.evaluate(parent_scope):
        return true_expr.evaluate(parent_scope)
    else:
        return false_expr.evaluate(parent_scope)

def expandArgs(parent_scope, *args):
    return [a.evaluate(parent_scope) for a in args]

def plusBuiltin(parent_scope, *args):
    x = expandArgs(parent_scope, args);
    return sum(x)

def minusBuiltin(parent_scope, *args):
    x = expandArgs(parent_scope, args);
    return reduce(operator.sub, x[1:], x[0])

def timesBuiltin(parent_scope, *args):
    x = expandArgs(parent_scope, args);
    return reduce(operator.mul, x, 1)

def divBuiltin(parent_scope, *args):
    x = expandArgs(parent_scope, args);
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


def make_datum(t):
    dtype, dval = t
    if dtype in ('BOOL', 'INT', 'FLOAT', 'STRING'):
        return StaticDatum(dval)
    elif dtype == 'ID':
        return VarRef(dval)
    elif dtype == 'SET':
        dval['value'] = make_datum(dval['value'])
        return Set(**dval)
    elif dtype == 'DEFUN':
        dval['body'] = make_datum(dval['body'])
        return FunctionDef(**dval)
    elif dtype == 'FUNC_CALL':
        dval['arg_exprs'] = [make_datum(a) for a in dval['arg_exprs'][1]]
        return FunctionCall(**dval)
    elif dtype == 'EXPRSEQ':
        return ExprSeq([make_datum(i) for i in dval])
    elif dtype == 'LIST':
        return List([make_datum(i) for i in dval])
    else:
        raise Exception("Unknown statement %s"%str(t))


class GlobalScope(Scope):
    def __init__(self, builtins):
        super().__init__()
        for id, f in builtins.items():
            self.assign(id, f)
