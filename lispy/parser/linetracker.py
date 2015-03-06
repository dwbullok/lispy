__author__ = 'Dan Bullok and Ben Lambeth'

from ..common import TokenPos
from codeviking.contracts import check_sig


@check_sig
class LineTracker(object):
    """Tracks line numbers and computes TokenPos tuples.  This only works if
    we ask for the token positions in the order they occur (this doesn't
    handle random access of token positions).
    """

    def __init__(self, unit_name: str):
        self._unit_name = unit_name
        self._last_line_offset = 0
        self._line = 0


    def inc_line(self, char_offset: int):
        """
        Records a newline.  This increments the line counter and records the
        character offset where the newline occurs.

        :param char_offset: the character offset (within the unit) of the
                            newline.
        :type char_offset: int
        """
        self._last_line_offset = char_offset
        self._line += 1

    def get_pos(self,
                char_offset: int) -> TokenPos:
        """
        Calculate a TokenPos for a given character offset within the unit.

        Note that we only support looking up the positions of tokens that
        occur AFTER the last newline we've tracked.

        :param char_offset: the character offset (within the unit) of the
                            start of the token
        :type char_offset: int

        :return: A TokenPos that indicates the position within the unit of
                 the given character offset.
        :rtype: TokenPos
        """

        assert (char_offset >= self._last_line_offset)
        return TokenPos(self._unit_name,
                        self._line + 1,
                        char_offset - self._last_line_offset + 1)
