from seecr.test import SeecrTestCase, CallTrace

from StringIO import StringIO

from weightless.core import be, compose
from meresco.core import Observable

from oas import ReindexIdentifier

def joco(gen):
    return ''.join(compose(gen))

class ReindexIdentifierTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace(emptyGeneratorMethods=['add'])
        self.dna = be(
            (Observable(),
                (ReindexIdentifier(),
                    (self.observer, )
                )
            )
        )

    def testEmptyIdentifier(self):
        header, body = joco(self.dna.all.handleRequest(arguments={'identifier': ['']})).split('\r\n'*2, 1)
        self.assertTrue('500' in header, header)
        self.assertEquals(0, len(self.observer.calledMethods))

    def testIdentifier(self):
        self.observer.returnValues['isAvailable'] = (True, True)
        self.observer.returnValues['getStream'] = StringIO("<xml/>")
        header, body = joco(self.dna.all.handleRequest(arguments={'identifier': ['an:identifier']})).split('\r\n'*2, 1)
        self.assertTrue('200' in header, header)
        self.assertEquals(['isAvailable', 'getStream', 'add'], [m.name for m in self.observer.calledMethods])
        kwargs = self.observer.calledMethods[2].kwargs
        self.assertEquals('an:identifier', kwargs['identifier'])
        self.assertEquals('rdf', kwargs['partname'])
        self.assertTrue('lxmlNode' in kwargs)

    def testIdentifierNotFound(self):
        self.observer.returnValues['isAvailable'] = (False, False)
        header, body = joco(self.dna.all.handleRequest(arguments={'identifier': ['an:identifier']})).split('\r\n'*2, 1)
        self.assertTrue('500' in header, header)
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEquals(['isAvailable'], [m.name for m in self.observer.calledMethods])
