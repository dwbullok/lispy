import unittest
from collections import namedtuple

from parser.scope import Scope, ArgExpr, FunctionDef, ExprSeq, List, \
    FunctionCall, Set, VarRef


class Expression(object):
    def evaluate(self, scope):
        return "I work"


MockEvaluate = namedtuple('MockEvaluate', 'evaluate value')


class TestScope(unittest.TestCase):
    def setUp(self):
        self.isolatedScope = Scope()
        self.parentScope = Scope()
        self.childScope = Scope(self.parentScope)

    def test_parent(self):
        self.assertEqual(self.isolatedScope.parent, None)
        self.assertEqual(self.childScope.parent, self.parentScope)
        self.assertEqual(self.parentScope.parent, None)

    def test_get(self):
        self.assertEqual(self.isolatedScope.get("something"), None)

        self.isolatedScope.assign("something", 5)
        self.assertEqual(self.isolatedScope.get("something"), 5)

        self.parentScope.assign("parentThing", 10)
        self.assertEqual(self.childScope.get("parentThing"), 10)

    def test_assign(self):
        self.parentScope.assign("x", 1)
        self.childScope.assign("x", 2)
        self.assertEqual(self.parentScope.get("x"), 2)

        self.childScope.create_local("x", 10)
        self.assertEqual(self.childScope.get("x"), 10)

        self.childScope.assign("x", 40)
        self.assertEqual(self.childScope.get("x"), 40)
        self.assertEqual(self.parentScope.get("x"), 2)

        self.assertRaises(Exception, self.childScope.create_local, ("x", 5))

    def test_lazy_eval(self):
        argExpr = ArgExpr(self.isolatedScope, Expression())
        self.isolatedScope.assign("argE", argExpr)
        self.assertEqual(self.isolatedScope.get("argE"), "I work")


class TestFunctionDef(unittest.TestCase):
    def test_evaluate(self):
        scope = Scope()
        f = FunctionDef(('ID', 'f'), [], None)
        f.evaluate(scope)
        self.assertEqual(scope.get('f'), f)

    def test_call(self):
        scope = Scope()
        f = FunctionDef(('ID', 'f'), [], Expression())
        self.assertEqual(f(scope), "I work")

        body = MockEvaluate(lambda scope: scope.get('x'), 1)
        g = FunctionDef(('ID', 'g'), [('ID', 'x')], body)
        self.assertEqual(g(scope, MockEvaluate(lambda x: 5, 1)), 5)


class TestExprSeq(unittest.TestCase):
    def test_evaluate(self):
        scope = Scope()
        f = lambda x: lambda y: x
        evals = [MockEvaluate(f(x), x) for x in range(10)]

        exprSeq = ExprSeq(evals)
        self.assertEqual(exprSeq.evaluate(scope), 9)
        self.assertEqual(exprSeq.value, list(range(10)))


class TestList(unittest.TestCase):
    def test_evaluate(self):
        scope = Scope()
        f = lambda x: lambda y: x
        evals = [MockEvaluate(f(x), x) for x in range(10)]

        exprSeq = List(evals)
        self.assertEqual(exprSeq.evaluate(scope), list(range(10)))
        self.assertEqual(exprSeq.value, list(range(10)))


class TestFunctionCall(unittest.TestCase):
    def test_evaluate(self):
        def makeDef(x):
            def f(scope, *args):
                return x

            return f

        scope = Scope()
        for x in "fgh":
            scope.assign(x, makeDef(x))
        for x in "fgh":
            funcCall = FunctionCall(('ID', x), [])
            self.assertEqual(funcCall.evaluate(scope), x)


class TestSet(unittest.TestCase):
    def test_evaluate(self):
        scope = Scope()
        mySet = Set(('ID', 'x'), MockEvaluate(lambda x: 10, 10))
        mySet.evaluate(scope)
        self.assertEqual(scope.get('x'), 10)


class TestVarRef(unittest.TestCase):
    def test_evaluate(self):
        scope = Scope()
        for x in "abcd":
            scope.assign(x, x)

        for x in "abcd":
            r = VarRef(x)
            self.assertEqual(r.evaluate(scope), x)


if __name__ == '__main__':
    unittest.main()
