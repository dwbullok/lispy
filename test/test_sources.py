__author__ = 'Dan Bullok and Ben Lambeth'

TEST_RESULT = (
    ("( ( + 1 2) ( + 2 1) )",
     [3, 3]),
    ("(1 3 4)", [1, 3, 4]),
    ("""((defun f (x) (+ x 2))
        (f 8))""",
     [None, 10]),
    ("( #t #f)",
     [True, False]),
    ("""(
          (defun f (x)
            (defun g (y) (+ x y 4.0))
            (+ (g 5) x 1)
          )
          ("homer" (f 2))
          (if (= 2 (f 3)) 6.7 "bart")
          (set x 2)
        )""",
     [None, ['homer', 14.0], 'bart', 2]),
    ("""(begin (set x 2) (if (= x 2) "yay" "nay"))""", "yay"),
    ("""(begin (defun fibb (n)
           (if (or (= n 0) (= n 1)) 1 (+ (fibb (- n 1)) (fibb (- n 2)))))
        (fibb 5))""", 8)
)

from lispy.interpreter import Interpreter
from lispy.interpreter.loader import DictLoader


def check_result(source, expected_result):
    loader = DictLoader({'main': source})
    interp = Interpreter(loader)
    test_result = interp.run_module('main')
    assert test_result == expected_result


# Test all the instances
def test_all():
    for (source, result) in TEST_RESULT:
        yield (check_result, source, result)

# TODO:  Add test cases that check for code that should fail.



