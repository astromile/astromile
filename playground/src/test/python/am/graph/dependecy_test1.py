import unittest


class Variable:
    def get_value(self):
        pass


class SimpleVariable(Variable):
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value


class Formula:
    def __init__(self, *dependencies: Variable):
        self.dependencies = dependencies
        self.computed_value = None
        self.computed_dependencies = None

    def value(self):
        computed_dependencies = [d.get_value() for d in self.dependencies]

        if self.computed_dependencies is None:
            changed = True
        else:
            changed = False
            for new_value, old_value in zip(computed_dependencies, self.computed_dependencies):
                if old_value != new_value:
                    changed = True
                    break
        if changed:
            self.computed_dependencies = computed_dependencies
            self.computed_value = self.evaluate()
        return self.computed_value

    def evaluate(self):
        pass


class Sum(Formula):
    def __init__(self, *terms):
        super().__init__(*terms)

    def evaluate(self):
        return sum(self.computed_dependencies)

class MyTestCase(unittest.TestCase):
    def test_sum(self):
        a = SimpleVariable(1)
        b = SimpleVariable(2)
        # noinspection PyShadowingBuiltins
        sum = Sum(a, b)
        self.assertEqual(3, sum.value())  # add assertion here
        a.value = 3
        self.assertEqual(5, sum.value())


if __name__ == '__main__':
    unittest.main()
