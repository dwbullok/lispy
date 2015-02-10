__author__ = 'Dan Bullok and Ben Lambeth'

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
        try:
            if self._parent is None:
                return self._defns[id]
            else:
                return self._defns.get(id, self._parent.get(id))
        except KeyError as e:
            return None

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


class Datum(object):
    def evaluate(self, parent_scope):
        pass


class StaticDatum(Datum):
    def __init__(self, value):
        self._value = value

    def evaluate(self, parent_scope):
        return self._value

    @property
    def value(self):
        return self._value


class FunctionDef(Datum):
    def __init__(self, name, args, body):
        self._name = name
        self._args = args
        self._body = body

    def call(self, parent_scope, arg_vals):
        assert(len(self._args)==len(arg_vals))
        scope = Scope(parent_scope)
        for (id, val) in zip(self._args, arg_vals):
            scope.assign(id, val)
        last_value = None
        for item in self._body:
            last_value = item.evaluate(scope)
        return last_value


def evaluate(self, parent_scope):
    parent_scope.assign(self._name, self)


class Sexp(Datum):
    def __init__(self, items):
        self._items = items
    def evaluate(self, parent_scope):
        last_value = None
        for item in self._items:
            last_value = item.evaluate(parent_scope)



"""
(defun f (x) (+ x 1))
(defun name1 (x) (+ x 1))
(set s "name1")
(`s 4)
(name1 4)

"""



class FunctionCall(Datum):
    def __init__(self, name, arg_vals):
        self._name = name[1]
        self._arg_vals = arg_vals

    def evaluate(self, parent_scope):
        func_def = parent_scope.get(self._name)
        if func_def is None:
            raise Exception("Undefined function '%s'" % str( self._name))

        return func_def.call(parent_scope, self._arg_vals)


class Set(Datum):
    def __init__(self, name, value):
        self._name =name
        self._value = value

    def evaluate(self, parent_scope):
        v = self._value.evaluate(parent_scope)
        parent_scope.assign(self._name, v)
        return v

class BuiltinFunction(Datum):
    def __init__(self, func):
        self._func = func

    def call(self, parent_scope, arg_vals):
        #TODO : if user redefines a builtin, we need to look up any
        # redefined funtions used within the body of func, and use those
        # instead of the builtins (we need to look in parent_scope for these).
        return self._func(*arg_vals)


def make_datum(t):
    dtype, dval = t
    if dtype in ('BOOL', 'INT', 'FLOAT', 'STRING'):
        return StaticDatum(dval)
    elif dtype == 'SET':
        return Set(**dval)
    elif dtype == 'DEFUN':
        return FunctionDef(**dval)
    elif dtype == 'FUNC_CALL':
        dval['arg_vals'] = [make_datum(a) for a in dval['arg_vals']]
        return FunctionCall(**dval)
    elif dtype == 'SEXP':
        return [make_datum(i) for i in dval]
    else:
        raise Exception("Unknown statement %s"%str(t))


