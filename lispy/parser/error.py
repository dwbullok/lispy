__author__ = 'dan'
from ..common import LispyError


class ParseError(LispyError):
    """
    Base class for errors issued from the parser.
    """

    def __init__(self, pos, message):
        """
        :param pos: the position in the source code where the error occurred.
            Use `None` location that is unknown or outside the source code.
        :type pos: `TokenPos` or `None`
        :param message: the error message
        :type message: str
        """
        super().__init__(pos, message)


class TokenError(ParseError):
    """
    Unable to tokenize text
    """

    def __init__(self, pos, text):
        """
        :param pos: the position in the source code where the error occurred.
            Use `None` location that is unknown or outside the source code.
        :type pos: `TokenPos` or `None`
        :param text: the text that the Tokenizer couldn't process
        :type text: str
        """
        super().__init__(pos, "Cannot parse text beginning with '%s'" % text)


class TooManyClosingParensError(ParseError):
    """
    Unable to find an opening parenthesis matching a closing parenthesis.
    """

    def __init__(self, pos):
        """
        :param pos: the position in the source code where the error occurred.
            Use `None` location that is unknown or outside the source code.
        :type pos: `TokenPos` or `None`
        """
        super().__init__(pos, "No corresponding opening parenthesis found.")


class UnclosedExpressionError(ParseError):
    """
    There are unclosed expressions on the stack.
    """

    def __init__(self, pos):
        """
        :param pos: the position in the source code where the error occurred.
            Use `None` location that is unknown or outside the source code.
        :type pos: `TokenPos` or ``None``
        """
        super().__init__(pos, "Unclosed Expression.")
