from collections import namedtuple
from .error import VarNameNotFoundError
from ..common import TokenPos, Syn

__author__ = 'Dan Bullok and Ben Lambeth'

ArgExpr = namedtuple('ArgExpr', 'parent_scope expr')
ArgExpr.evaluate = lambda s: s.expr.evaluate(s.parent_scope)


class Scope(object):
    '''
    Represents scope.  Contains definitions bound to identifiers.
    '''

    def __init__(self, pos, parent=None):
        '''
        :param pos:  source position where the scope begins
        :type pos: LexicalPos
        :param parent: parent scope that contains this scope
        :type parent: Scope (or None)
        '''
        assert isinstance(pos, TokenPos)
        assert (parent is None) or isinstance(parent, Scope)
        self._defns = dict()
        self._parent = parent

    @property
    def parent(self):
        '''
        :return: The scope containing this one, or None if this is a
        top-level scope
        :rtype: Scope
        '''
        return self._parent

    def get(self, id):
        '''
        Retrieve the definition of an identifier.  Look in the local scope,
        then ancestor scopes.

        :param id: identifier to look up.
        :type id: Syn (id.value must be a str)
        :return: the definition of the given identifier
        :rtype: datatypes.Datum or ArgExpr
        :throws VarNameNotFoundError: if identifier is not found in this
        or any ancestor scope
        '''
        assert isinstance(id, Syn)
        defn = None
        if self._parent is not None:
            if id.value in self._defns:
                defn = self._defns[id.value]
            else:
                return self._parent.get(id)
        else:
            if id.value in self._defns:
                defn = self._defns[id.value]
            else:
                raise VarNameNotFoundError(id.pos, id.value)
        if isinstance(defn, ArgExpr):
            # handle lazy arg evaluation
            return defn.expr.evaluate(defn.parent_scope)
        else:
            return defn

    def assign(self, id, defn):
        '''
        Assign a definition to an identifier.

        This assignment follows the usual scope rules:
            * If the identifier is not defined in this scope or any of its
              parents, a new identifier is created within this scope.
            * Otherwise, the definition assigned to the identifier in the first
              parent scope is overwritten.

        :param id: identifier to bind to
        :type id: id.value must be a str
        :param defn: the definition to bind to id
        :type defn: datatypes.Datum or python primitive type (is_valid_defn(
        defn) must be true.
        '''
        assert (isinstance(id, Syn))
        assert (is_valid_defn(defn))

        if id.value in self._defns:
            self._defns[id.value] = defn
            return
        try:
            dummy = self.get(id)
        except VarNameNotFoundError as e:
            self._defns[id.value] = defn
        else:
            # id has been defined in a parent.
            self._parent.assign(id, defn)

    def create_local(self, id, defn):
        '''
        Create a new binding from id to defn in this scope.  Parent scopes
        are not searched for an instance of id.

        :param id: identifier to bind to
        :type id: id.value must be a str
        :param defn: the definition to bind to id
        :type defn: datatypes.Datum
        :throws AssignmentError: if id already has a binding in this scop
        '''
        assert (isinstance(id, Syn))
        assert (is_valid_defn(defn))
        if id in self._defns:
            raise Exception(
                "Can't create a variable that has already been defined: %s" %
                id)
        self._defns[id.value] = defn


'''
A pseudo-position where all the global builtins are defined.
'''
__BUILTIN_POS__ = TokenPos('__BUILTINS__', 0, 0)


class GlobalScope(Scope):
    '''A top level global Scope
    '''

    def __init__(self, builtins):
        '''
        :param builtins:
        :type builtins: dict[str,function]
        :return:
        :rtype:
        '''
        super().__init__(__BUILTIN_POS__)
        # a fake position
        for id, f in builtins.items():
            # create an ID to use for binding.
            self.create_local(Syn('ID', id, __BUILTIN_POS__), f)


class Datum(object):
    def __init__(self, pos):
        '''
        :param pos: the source position where this Datum occurs
        :type pos: LexicalPos
        '''
        self._pos = pos

    def evaluate(self, parent_scope):
        '''
        Evaluate this Datum in the given parent scope.

        :param parent_scope: the scope in which this Datum is evaluated
        :type parent_scope: Scope
        :return: The result of the evaluation.
        '''
        pass

    @property
    def value(self):
        '''
        :return the value of this Datum (for literals, this is the value of
        the literal (no evaluation takes place).
        '''
        return self

    @property
    def pos(self):
        return self._pos

    def __str__(self):
        return str(self.value)


VALID_DEFNS = (Datum, int, float, str, bool, complex, ArgExpr)


def is_evaluatable(obj):
    '''
    Determine whether obj can be evaluated.

    :param obj: the object to check
    :param obj: any
    :return: True if obj has an evaluate method.  False otherwise
    :rtype: bool
    '''
    return hasattr(obj, 'evaluate')


def is_valid_defn(obj):
    return (type(obj) in VALID_DEFNS) or is_evaluatable(obj) or callable(obj)

