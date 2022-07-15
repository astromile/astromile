import unittest

import numpy as np


class Value:
    def get_value(self):
        pass


class Listener:
    def notify(self, observable):
        pass


# noinspection PyRedeclaration
class Observable(Value):
    def __init__(self, value=None):
        self.listeners = []
        self.value = value

    def add_listener(self, listener: Listener):
        self.listeners.append(listener)

    def notify_all(self):
        for listener in self.listeners:
            listener.notify(self)

    def same_as(self, value):
        if self.value is None:
            return value is None
        elif value is None:
            return False
        else:
            return self.equals(self.value, value)

    def equals(self, x, y):
        return x == y

    def __add__(self, other):
        return Sum(self, other)

    def __mul__(self, other):
        return Product(self, other)


class Variable(Observable):
    def __init__(self, value=None):
        super().__init__(value)
        self.listeners = []

    def get_value(self):
        return self.value

    def set_value(self, value):
        changed = not self.same_as(value)
        self.value = value
        if changed:
            self.notify_all()


class Composite(Listener, Observable):
    def __init__(self, formula, *parameters: Observable):
        super().__init__()

        self.formula = formula
        self.parameters = parameters

        self.updated = set(parameters)
        self.cache = {}

        for parameter in parameters:
            parameter.add_listener(self)

    def notify(self, observable):
        self.notify_all()
        self.updated.add(observable)

    def get_value(self):
        changed = False
        for parameter in self.updated:
            new_value = parameter.get_value()
            old_value = self.cache.get(parameter, None)
            if not parameter.same_as(old_value):
                changed = True
            self.cache[parameter] = new_value
        self.updated = set()
        if changed:
            self.value = self.formula(*[self.cache[parameter] for parameter in self.parameters])
        return self.value


class Sum(Composite):
    def __init__(self, *terms):
        super().__init__(lambda *x: sum(x), *terms)


class Product(Composite):
    def __init__(self, *factors):
        super().__init__(lambda *x: np.product(x), *factors)


class MyTestCase(unittest.TestCase):
    def test_sum(self):
        a = Variable(1)
        b = Variable(2)
        c = Variable(3)
        d = Variable(4)
        # noinspection PyShadowingBuiltins
        apb = a + b
        abc = a * b * c
        self.assertEqual(3, apb.get_value())  # add assertion here
        self.assertEqual(6, abc.get_value())
        a.set_value(3)
        c.set_value(1)
        self.assertEqual(5, apb.get_value())
        self.assertEqual(6, abc.get_value())



if __name__ == '__main__':
    unittest.main()
