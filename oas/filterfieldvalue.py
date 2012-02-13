from weightless.core import Observable
from meresco.core import Transparent

class FilterFieldValue(Transparent):
    def __init__(self, method):
        Transparent.__init__(self)
        self._method = method

    def addField(self, name, value):
        if self._method(value):
            self.do.addField(name=name, value=value)
