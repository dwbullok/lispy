__author__ = 'Dan Bullok and Ben Lambeth'
'''
Elements common to the parser and the interpreter.
'''
from collections import namedtuple


TokenPos = namedtuple('TokenPos', 'unit_name line column')
'''
:param unit_name: the compilation unit (usually a file name)
:type unit_name: str
:param line: line number within the unit (starting at 1)
:type line: int
:param column: column number within the line (starting at 1)
:type column: int
'''

# add a string conversion
TokenPos.__str__ = lambda s: '%s:%d:%d' % (s.unit_name, s.line, s.column)

Syn = namedtuple('Syn', 'type value pos')
'''
:param type: type of the token
:type type: str
:param value: the value of the token
:type value: any
:param pos: position of the token within the source
:type pos: TokenPos
'''

AstNode = namedtuple('AstNode', 'type value pos')
'''
:param type: type of the AstNode
:type type: str
:param value: the value of the AstNode
:type value: any
:param pos: position of the token within the source
:type pos: TokenPos
'''





class LispyException(Exception):
    '''Base class for all Lispy exceptions.
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


class LispyError(LispyException):
    '''Base class for errors that should be reported to the user.
    '''

    def __init__(self, pos, message):
        '''
         :param pos: the position in the source code where the error occurred.
                Use `None` location that is unknown or outside the source code.
         :type pos: `TokenPos` or `None`
         :param message: the error message
         :type message: str
         '''

        self._pos = pos
        self._message = message


    @property
    def pos(self):
        '''The position (`TokenPos`) where the error occurred.
        '''
        return self._pos


    @property
    def message(self):
        '''
        The message.  There is no need to include position information in the
         message.  Position information will be prefixed to the method automatically.

        '''
        return self._message

    def __str__(self):
        if self.pos is None:
            return 'Error:\n%s' % self.message
        return 'Error at %s:%d,%d\n%s' % (self.pos.unit_name,
                                          self.pos.line,
                                          self.pos.column,
                                          self.message)
