from collections import namedtuple
from .error import VarNameNotFoundError
from ..common import TokenPos, Syn, AstNode

__author__ = 'Dan Bullok and Ben Lambeth'

from ..common import ArgExpr

from .datatypes import Symbol, is_valid_defn

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

    def make_child_scope(self, pos):
        return Scope(pos, self)

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

        name = None
        if isinstance(id, Symbol):
            id = id._name
        name = id.value
        if not isinstance(name, str):
            raise Exception("FUUUUUUUUUUCCCKKKKK!")


        defn = None
        if self._parent is not None:
            if name in self._defns:
                defn = self._defns[name]
            else:
                return self._parent.get(id)
        else:
            if name in self._defns:
                defn = self._defns[name]
            else:
                raise VarNameNotFoundError(id.pos, name)
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

    def __init__(self, builtins, interpreter_builtins, interpreter):
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
        for id, make_func in interpreter_builtins.items():
            # create an ID to use for binding.
            bulitin_func = make_func(interpreter)
            self.create_local(Syn('ID', id, __BUILTIN_POS__), bulitin_func)

