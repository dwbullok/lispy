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
        (fibb 5))""", 8),
    ({'main': """(begin
                  (load "external_thinggie")
                  (ext 3)
                 )""",
     'external_thinggie': "(defun ext (x) (+ x 1))"},
    4)
)

FILE_RESULT = (('test1.lisp', [3, 3]),)


from lispy.interpreter import Interpreter
from lispy.interpreter.loader import DictLoader, FileSysLoader
import os

def check_result(source, expected_result):
    loader_dict = {}
    if isinstance(source, str):
        loader_dict = {'main': source}
    elif isinstance(source, dict):
        loader_dict = source
    loader = DictLoader(loader_dict)
    interp = Interpreter(loader)
    test_result = interp.run_module('main')
    assert test_result == expected_result


def file_check_result(file_name, expected_result):
    cwd = os.getcwd()
    loader = FileSysLoader([os.path.join(cwd,'source_file_tests')])
    interp = Interpreter(loader)
    test_result = interp.run_module(file_name)
    assert test_result == expected_result


# Test all the instances
def nottest_all_dict():
    for (source, result) in TEST_RESULT:
        yield (check_result, source, result)

# Test all the instances on the file system
def nottest_all_files():
    for (file_name, result) in FILE_RESULT:
        yield (file_check_result, file_name, result)


from pprint import PrettyPrinter

P = PrettyPrinter(indent=4)

from lispy.parser.tokenizer import Tokenizer
# TODO:  Add test cases that check for code that should fail.
def test_print_tokens():
    tokenizer = Tokenizer()
    for (source, result) in TEST_RESULT:
        if isinstance(source, str):
            print(('-'*80)+'\n'+source+'\n')
            P.pprint(tokenizer.tokenize('main', source))

test_print_tokens()

