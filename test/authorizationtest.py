from seecr.test import SeecrTestCase, CallTrace

from weightless.core import be, compose
from meresco.core import Observable

from oas import Authorization

class AuthorizationTest(SeecrTestCase):
    def testOne(self):
        class Intercept(Observable):
            def handleRequest(self, **kwargs):
                self.authorization = self.ctx.authorization
                return
                yield

        intercept = Intercept()
        dna = be(
            (Observable(),
                (Authorization(),
                    (intercept,)
                )
            )
        )
        list(compose(dna.all.handleRequest(Headers={'Authorization': 'ThisIsTheApiKey'})))

        self.assertEquals({'apikey': 'ThisIsTheApiKey'}, intercept.authorization)
