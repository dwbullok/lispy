__author__ = 'dan'

EXAMPLE = """
(begin
  (defun f (x)
    (defun g (y) (+ x y 4.0))
    (+ (g 5) x 1)
  ) ;a test comment ...
  (list
    (f 2)
    (f 3)
  )
)"""


def tokens_match(a, b):
    return a.stype == b.stype and a.value == b.value


TOKENS = [  # 1
            ('LPAREN', '('),
            ('ID', 'begin'),
            # 2
            ('LPAREN', '('),
            ('ID', 'defun'),
            ('ID', 'f'),
            ('LPAREN', '('),
            ('ID', 'x'),
            ('RPAREN', ')'),
            # 3
            ('LPAREN', '('),
            ('ID', 'defun'),
            ('ID', 'g'),
            ('LPAREN', '('),
            ('ID', 'y'),
            ('RPAREN', ')'),
            ('LPAREN', '('),
            ('ID', '+'),
            ('ID', 'x'),
            ('ID', 'y'),
            ('FLOAT', 4.0),
            ('RPAREN', ')'),
            ('RPAREN', ')'),
            # 4
            ('LPAREN', '('),
            ('ID', '+'),
            ('LPAREN', '('),
            ('ID', 'g'),
            ('INT', 5),
            ('RPAREN', ')'),
            ('ID', 'x'),
            ('INT', 1),
            ('RPAREN', ')'),
            # 5
            ('RPAREN', ')'),
            # 6
            ('LPAREN', '('),
            ('ID', 'list'),
            # 7
            ('LPAREN', '('),
            ('ID', 'f'),
            ('INT', 2),
            ('RPAREN', ')'),
            # 8
            ('LPAREN', '('),
            ('ID', 'f'),
            ('INT', 3),
            ('RPAREN', ')'),
            # 9
            ('RPAREN', ')'),
            ('RPAREN', ')')
]

from copy import copy
from lispy.interpreter import Tokenizer, Parser
from lispy.common import Syn, AstNode, TokenPos

from pprint import PrettyPrinter

P = PrettyPrinter(indent=4)


def test_tokenizer():
    tokenizer = Tokenizer()
    tokens = tokenizer.tokenize('main', EXAMPLE)
    expected_tokens = copy(TOKENS)
    tpos = TokenPos('test',1,1)
    while len(tokens) > 0:
        tt = tokens.pop(0)
        et = Syn(*(TOKENS.pop(0) + (tpos,)))
        print((tt, et))
        assert tokens_match(tt, et)

    assert len(tokens) == 0
    assert len(TOKENS) == 0


def test_parser():
    tokenizer = Tokenizer()
    parser = Parser()
    tokens = tokenizer.tokenize('main', EXAMPLE)
    pprint_node(parser.parse(tokens))


def pprint_node(node, indent=0):
    PFX = ' ' * indent
    if isinstance(node, list):
        for n in node:
            pprint_node(n, indent + 4)
    elif isinstance(node, AstNode):
        print(PFX + 'A:' + node.stype + '\t' + str(node.pos))
        pprint_node(node.value, indent + 4)
    elif isinstance(node, Syn):
        print(PFX + 'S:' + node.stype + '\t[' + str(
            node.value) + ']\t' + str(node.pos))
    else:
        print(PFX + type(node).__name__ + '(' + str(node) + ')')


if __name__ == '__main__':
    test_tokenizer()
    test_parser()

