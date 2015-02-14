__author__ = 'Dan Bullok and Ben Lambeth'
'''
Elements common to the parser and the interpreter.
'''
from collections import namedtuple

'''
Attributes:
    unit_name: the compilation unit (usually a file name)
    line: line number within the unit (starting at 1)
    column: column number within the line (starting at 1)
'''
TokenPos = namedtuple('TokenPos', 'unit_name line column')
# add a string conversion
TokenPos.__str__ = lambda s: '%s:%d:%d' % (s.unit_name, s.line, s.column)

'''
Simple syntactical element.
'''
Syn = namedtuple('Syn', 'type value pos')


class LispyException(Exception):
    '''Base class for all Lispy exceptions
    '''

    def __init__(self, pos, message):
        '''
        :param pos: position where the error occurs
        :type pos: TokenPos
        :param message: the error message
        :type message: str
        '''
        super().__init__(message)
        self._message = message
        self._pos = pos

    def __str__(self):
        return 'Error: %s at %s:' % (self._message, self._pos)
