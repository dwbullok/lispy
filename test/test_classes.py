import unittest
from collections import namedtuple

from lispy.interpreter.scope import Scope
from lispy.interpreter.datatypes import ExprSeq, List, \
    FunctionCall, Symbol
from lispy.common import Syn, TokenPos, ArgExpr
from lispy.interpreter.error import VarNameNotFoundError


class Expression(object):
    def __init__(self, value):
        self.value = value

    def evaluate(self, scope):
        return self.value


class FuncExpression(Expression):
    def __init__(self, func):
        super().__init__(func)
        self._func = func

    def __call__(self, *args):
        return self._func(*args)


MockEvaluate = namedtuple('MockEvaluate', 'evaluate value')
dummy_pos = TokenPos('TEST', 0, 0)


def ID(id):
    return Syn('ID', id, dummy_pos)


class TestScope(unittest.TestCase):
    def setUp(self):
        self.isolatedScope = Scope(dummy_pos)
        self.parentScope = Scope(dummy_pos)
        self.childScope = Scope(dummy_pos, self.parentScope)

    def test_parent(self):
        self.assertEqual(self.isolatedScope.parent, None)
        self.assertEqual(self.childScope.parent, self.parentScope)
        self.assertEqual(self.parentScope.parent, None)

    def test_get(self):
        s = ID('something')
        p = ID('parentThing')
        self.assertRaises(VarNameNotFoundError, self.isolatedScope.get, s)

        self.isolatedScope.assign(s, 5)
        self.assertEqual(self.isolatedScope.get(s), 5)

        self.parentScope.assign(p, 10)
        self.assertEqual(self.childScope.get(p), 10)

    def test_assign(self):
        x = ID('x')
        self.parentScope.assign(x, 1)
        self.childScope.assign(x, 2)
        self.assertEqual(self.parentScope.get(x), 2)

        self.childScope.create_local(x, 10)
        self.assertEqual(self.childScope.get(x), 10)

        self.childScope.assign(x, 40)
        self.assertEqual(self.childScope.get(x), 40)
        self.assertEqual(self.parentScope.get(x), 2)

        self.assertRaises(Exception, self.childScope.create_local, (x, 5))

    def test_lazy_eval(self):
        argExpr = ArgExpr(self.isolatedScope, Expression("I work"))
        self.isolatedScope.assign(ID("argE"), argExpr)
        self.assertEqual(self.isolatedScope.get(ID("argE")), "I work")
#
#
# class TestFunctionDef(unittest.TestCase):
#     def test_evaluate(self):
#         scope = Scope(dummy_pos)
#         f = FunctionDef(dummy_pos, ID('f'), [], None)
#         f.evaluate(scope)
#         self.assertEqual(scope.get(ID('f')), f)
#
#     def test_call(self):
#         scope = Scope(dummy_pos)
#         f = FunctionDef(dummy_pos, ID('f'), [], Expression("I work"))
#         self.assertEqual(f(scope), "I work")
#
#         body = MockEvaluate(lambda scope: scope.get(ID('x')), 1)
#         g = FunctionDef(dummy_pos, ID('g'), [ID('x')], body)
#         self.assertEqual(g(scope, MockEvaluate(lambda x: 5, 5)), 5)


class TestExprSeq(unittest.TestCase):
    def test_evaluate(self):
        scope = Scope(dummy_pos)
        f = lambda x: lambda y: x
        evals = [MockEvaluate(f(x), x) for x in range(10)]

        exprSeq = ExprSeq(dummy_pos, evals)
        self.assertEqual(exprSeq.evaluate(scope), 9)
        self.assertEqual(exprSeq.value, list(range(10)))


class TestList(unittest.TestCase):
    def test_evaluate(self):
        scope = Scope(dummy_pos)
        f = lambda x: lambda y: x
        evals = [MockEvaluate(f(x), x) for x in range(10)]

        exprSeq = List(dummy_pos, evals)
        self.assertEqual(exprSeq.evaluate(scope), list(range(10)))
        self.assertEqual(exprSeq.value, list(range(10)))


class TestFunctionCall(unittest.TestCase):
    def test_evaluate(self):
        def makeDef(x):
            def f(scope, *args):
                return x

            return FuncExpression(f)

        scope = Scope(dummy_pos)
        for x in "fgh":
            scope.assign(ID(x), makeDef(x))
        for x in "fgh":
            funcCall = FunctionCall(dummy_pos, ID(x), [])
            self.assertEqual(funcCall.evaluate(scope), x)

#
# class TestSet(unittest.TestCase):
#     def test_evaluate(self):
#         scope = Scope(dummy_pos)
#         mySet = Set(dummy_pos, ID('x'), MockEvaluate(lambda x: 10,
#                                                      10))
#         mySet.evaluate(scope)
#         self.assertEqual(scope.get(ID('x')), 10)
#
#
class TestSymbol(unittest.TestCase):
    def test_evaluate(self):
        scope = Scope(dummy_pos)
        for x in "abcd":
            scope.assign(ID(x), x)

        for x in "abcd":
            r = Symbol(dummy_pos, ID(x))
            self.assertEqual(r.evaluate(scope), x)


if __name__ == '__main__':
    unittest.main()
