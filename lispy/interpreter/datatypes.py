__author__ = 'Dan Bullok and Ben Lambeth'

from .scope import Scope, ArgExpr, Datum


'''
Data types.  These are built from the AST that the parser outputs.
'''


class FunctionDef(Datum):
    '''
    A function definition.
    '''

    def __init__(self, pos, name, args, body):
        '''
        :param name: the name to bind this function definition
        :type name: name.value must be a str
        :param args: the arguments this function takes
        :type args: a list of identifier tokens
        :param body: the body of the function
        :type body: ExprSeq
        '''
        super().__init__(pos)

        self._name = name
        self._args = [a for a in args]
        self._body = body

    def __call__(self, parent_scope, *arg_vals):
        assert (len(self._args) == len(arg_vals))
        scope = Scope(self.pos, parent_scope)
        for (id, val) in zip(self._args, arg_vals):
            # we store the values of the args - they might not actually be
            # computed.  This allows lazy evaluation of function args
            scope.create_local(id, ArgExpr(parent_scope, val))
        return self._body.evaluate(scope)
        # last_value = None
        # for item in self._body:
        # last_value = item.evaluate(scope)
        # return last_value

    @property
    def value(self):
        return 'FunctionDef %s (%s) at %s' % (self._name,
                                              [a.value for a in self._args],
                                              str(self.pos) )

    def evaluate(self, parent_scope):
        parent_scope.assign(self._name, self)


class FunctionCall(Datum):
    def __init__(self, pos, name, arg_exprs):
        super().__init__(pos)
        self._name = name
        self._arg_exprs = arg_exprs

    def evaluate(self, parent_scope):
        func_def = parent_scope.get(self._name)
        if func_def is None:
            raise Exception("Undefined function '%s'" % str(self._name))

        return func_def(parent_scope, *self._arg_exprs)


class ExprSeq(Datum):
    def __init__(self, pos, items):
        super().__init__(pos)
        self._items = items

    def evaluate(self, parent_scope):
        scope = Scope(self.pos, parent_scope)
        last_value = None
        for e in self._items:
            last_value = e.evaluate(scope)
        return last_value

    @property
    def value(self):
        return [i.value for i in self._items]


class List(ExprSeq):
    def evaluate(self, parent_scope):
        return [i.evaluate(parent_scope) for i in self._items]


class Set(Datum):
    def __init__(self, pos, name, value):
        super().__init__(pos)
        self._name = name
        self._value = value

    def evaluate(self, parent_scope):
        v = self._value.evaluate(parent_scope)
        parent_scope.assign(self._name, v)
        return v


class StaticDatum(Datum):
    '''
    Datum that represents a static (constant) value.
    '''

    def __init__(self, pos, value):
        '''
        :param value: the value of this StaticDatum
        :type value: the type of the literal value
        '''
        super().__init__(pos)
        self._value = value

    def evaluate(self, parent_scope):
        return self._value

    @property
    def value(self):
        return self._value


from ..common import Syn


class VarRef(Datum):
    def __init__(self, pos, name):
        '''
        :param pos: position of the variable reference within the source
        :type pos: TokenPos
        :param name: a Syn  with type='ID'
        :type name: Syn
        '''
        super().__init__(pos)
        assert isinstance(name, Syn)
        self._name = name

    def evaluate(self, parent_scope):
        return parent_scope.get(self._name)
