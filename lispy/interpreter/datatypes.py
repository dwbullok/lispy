__author__ = 'Dan Bullok and Ben Lambeth'

from ..common import Syn, TokenPos, ArgExpr


from codeviking.contracts import check_sig, Any

'''
Data types.  These are built from the AST that the parser outputs.
'''


class Datum(object):
    def __init__(self, pos):
        """
        :param pos: the source position where this Datum occurs
        :type pos: LexicalPos
        """
        self._pos = pos

    def evaluate(self, parent_scope):
        """
        Evaluate this Datum in the given parent scope.

        :param parent_scope: the scope in which this Datum is evaluated
        :type parent_scope: Scope
        :return: The result of the evaluation.
        """
        pass

    @property
    def value(self):
        """
        :return the value of this Datum (for literals, this is the value of
        the literal (no evaluation takes place).
        """
        raise NotImplementedError("value is not implemented for class "
                                  "%s" % self.__class__.__name__)

    @property
    def pos(self):
        return self._pos

    def __str__(self):
        return str(self.value)


VALID_DEFNS = (Datum, int, float, str, bool, complex, ArgExpr)


def is_evaluatable(obj):
    """
    Determine whether obj can be evaluated.

    :param obj: the object to check
    :param obj: any
    :return: True if obj has an evaluate method.  False otherwise
    :rtype: bool
    """
    return hasattr(obj, 'evaluate')


def is_valid_defn(obj):
    return (type(obj) in VALID_DEFNS) or is_evaluatable(obj) or callable(obj)


class ArgList(object):
    def __init__(self, args):
        self._args = []
        # for a in args:


# default_arg_transform = ArgExpr
# iquote_arg_transform = lambda s: SQUOTE(s)

''' (defun %defun %args %body
    )
'''


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
        scope = parent_scope.make_child_scope(self.pos)
        last_value = None
        for e in self._items:
            last_value = e.evaluate(scope)
        return last_value

    @property
    def value(self):
        return [i.value for i in self._items]


class Quote(Datum):
    def __init__(self, pos, value):
        super().__init__(pos)
        self._value = value

    def evaluate(self, parent_scope):
        return self._value


class List(ExprSeq):
    def evaluate(self, parent_scope):
        name = self._items[0].value
        func_def = parent_scope.get(name)
        if func_def is None:
            raise Exception("Undefined function '%s'" % str(name))
        return func_def(parent_scope, *[i.evaluate(parent_scope) for i in
                                        self._items])


@check_sig
class StaticDatum(Datum):
    """
    Datum that represents a static (constant) value.
    """

    def __init__(self, pos:TokenPos, value:Any):
        """
        :param value: the value of this StaticDatum
        :type value: the type of the literal value
        """
        super().__init__(pos)
        self._value = value

    def evaluate(self, parent_scope):
        return self._value

    @property
    def value(self):
        return self._value


class Symbol(Datum):
    def __init__(self, pos, name):
        """
        :param pos: position of the variable reference within the source
        :type pos: TokenPos
        :param name: a Syn  with type='ID'
        :type name: Syn
        """
        super().__init__(pos)
        assert isinstance(name, Syn)
        self._name = name

    @property
    def value(self):
        return self._name

    def evaluate(self, parent_scope):
        return parent_scope.get(self._name)


