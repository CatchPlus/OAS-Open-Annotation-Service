from seecr.test import SeecrTestCase, CallTrace

from weightless.core import be, compose
from meresco.components.http.utils import unauthorizedHtml
from meresco.core import Observable

from oas import ApiKeyCheck

class ApiKeyCheckTest(SeecrTestCase):
    def testOne(self):
        dna = be(
            (Observable(),
                (ApiKeyCheck(),)
            )
        )

        response = list(compose(dna.all.handleRequest()))
        self.assertEquals([unauthorizedHtml], response)

    def testUnknownApikey(self):
        def getForApikey(apikey):
            return None
        observer = CallTrace(
            methods={'getForApikey': getForApikey}, 
            emptyGeneratorMethods=['handleRequest'])

        class MockSetVar(Observable):
            def __init__(self):
                Observable.__init__(self)
        __callstack_var_authorization__ = {'apikey': "APIKEY"}

        dna = be(
            (MockSetVar(),
                (ApiKeyCheck(),
                    (observer, )
                )
            )
        )
        response = list(compose(dna.all.handleRequest()))
        self.assertEquals([unauthorizedHtml], response)
        self.assertEquals(['getForApikey'], [m.name for m in observer.calledMethods])
