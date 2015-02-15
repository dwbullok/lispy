from ..common import LispyException, TokenPos

__author__ = 'Dan Bullok and Ben Lambeth'


class LispyError(LispyException):
    '''Base class for errors that should be reported to the user.
    '''

    def __init__(self, pos, message):
        '''
        :param pos: the position in the source code where the error occurred.
               Use `None` location that is unknown or outside the source code.
        :type pos: TokenPos or None
        :param message: the error message
        :type message: str
        '''
        self._pos = pos
        self._message = message


    @property
    def pos(self):
        '''h
        '''
        return self._pos

    @property
    def message(self):
        return self._message

    def __str__(self):
        if self.pos is None:
            return 'Error:\n%s' % self.message
        return 'Error at %s:%d,%d\n%s' % (self.pos.unit_name,
                                          self.pos.line,
                                          self.pos.column,
                                          self.message)


class VarNameNotFoundError(LispyError):
    '''
    Unable to find the given variable name in the current scope.
    '''

    def __init__(self, pos, var_name):
        '''

        '''
        super().__init__(pos, 'Variable name "%s" not found' % var_name)


class CreateExistingVarNameError(LispyError):
    '''
    Can't create a new binding to a name that already exists in the current
    scope.
    '''
    # TODO: This might be something that shouldn't be passed to the user.  It
    # depends on whether a createvar feature is implemented in the language.
    # In either case, it might make sense to also show where the variable
    # we're trying to overwrite was initially created.
    def __init__(self, pos, var_name):
        super().__init__(pos, 'Variable name "%s" already exists in the '
                              'containing scope.  It cannot be created again '
                              'in this scope.' % var_name)


class UnitNotFoundError(LispyError):
    '''
    Unable to find a source code unit.
    '''

    def __init__(self, pos, unit_name):
        super().__init__(pos, 'Unit "%s" not found.' % unit_name)
        self._unit_name = unit_name



