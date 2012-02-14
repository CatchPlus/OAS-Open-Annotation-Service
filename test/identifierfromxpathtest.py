from seecr.test import SeecrTestCase, CallTrace
from lxml.etree import parse
from StringIO import StringIO

from weightless.core import compose, be
from meresco.core import Observable

from oas import IdentifierFromXPath

class IdentifierFromXPathTest(SeecrTestCase):

    def testOne(self):
        observer = CallTrace(emptyGeneratorMethods=['add'])
        dna = be(
            (Observable(),
                (IdentifierFromXPath("/a/@b"),
                    (observer,)
                )
            )
        )

        list(compose(dna.all.add(identifier="wrong", partname="xxx", lxmlNode=parse(StringIO("<a b='right'/>")))))
        self.assertEquals("right", observer.calledMethods[0].kwargs['identifier'])


    def testTwo(self):
        observer = CallTrace(emptyGeneratorMethods=['add'])
        dna = be(
            (Observable(),
                (IdentifierFromXPath("/a/@b"),
                    (observer,)
                )
            )
        )

        try:
            list(compose(dna.all.add(identifier="wrong", partname="xxx", lxmlNode=parse(StringIO("<a x='right'/>")))))
            self.fail()
        except ValueError, e:
            self.assertEquals("Identifier not found", str(e))
