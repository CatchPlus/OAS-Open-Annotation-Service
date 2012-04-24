## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
# Copyright (C) 2012 Meertens Instituut (KNAW) http://meertens.knaw.nl
# Copyright (C) 2012 Seecr (Seek You Too B.V.) http://seecr.nl
# 
# This file is part of "Open Annotation Service"
# 
# "Open Annotation Service" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# "Open Annotation Service" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with "Open Annotation Service"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# 
## end license ##

from seecr.test import SeecrTestCase, CallTrace

from weightless.core import be, compose
from meresco.core import Observable

from lxml.etree import parse, tostring
from StringIO import StringIO

from oas import Deanonymize

from testutil import lico

class DeanonymizeTest(SeecrTestCase):

    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace(emptyGeneratorMethods=['process'])
        self.deanonymize = Deanonymize()
        self.dna = be(
            (Observable(),
                (self.deanonymize,
                    (self.observer,)
                )
            )
        )

    def testPassThroughAbout(self):
        xml = """<rdf:RDF 
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:oac="http://www.openannotation.org/ns/"> 
    <oac:Annotation rdf:about="urn:id:1"/>
</rdf:RDF>"""

        lico(self.dna.all.process(lxmlNode=parse(StringIO(xml))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS(xml, tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))

    def testPassThroughResource(self):
        xml = """<rdf:RDF 
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:oac="http://www.openannotation.org/ns/"> 
    <oac:Annotation rdf:resource="urn:id:1"/>
</rdf:RDF>"""

        lico(self.dna.all.process(lxmlNode=parse(StringIO(xml))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS(xml, tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))

    def testAddUrn(self):
        xml = """<rdf:RDF 
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:oac="http://www.openannotation.org/ns/"> 
    <oac:Annotation%s/>
</rdf:RDF>"""

        newIdentifier = 'urn:some:form:of:identifier'
        self.deanonymize._urnGen = lambda: newIdentifier
        lico(self.dna.all.process(lxmlNode=parse(StringIO(xml % ""))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS(xml % ' rdf:about="%s"' % newIdentifier, tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))

    def testAddUrnToOacBody(self):
        xml = """<rdf:RDF 
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:oac="http://www.openannotation.org/ns/"> 
    <oac:Annotation rdf:about="urn:annotation:identifier">
        <oac:hasBody>
            <oac:Body%s/>
        </oac:hasBody>
    </oac:Annotation>
</rdf:RDF>"""

        newIdentifier = 'urn:some:form:of:identifier'
        self.deanonymize._urnGen = lambda: newIdentifier
        lico(self.dna.all.process(lxmlNode=parse(StringIO(xml % ""))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS(xml % ' rdf:about="%s"' % newIdentifier, tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))


    def testAddUrnToOacConstrainedTarget(self):
        xml = """<rdf:RDF 
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:oac="http://www.openannotation.org/ns/"> 
    <oac:Annotation rdf:about="urn:annotation:identifier">
        <oac:hasTarget>
            <oac:ConstrainedTarget%s/>
        </oac:hasTarget>
    </oac:Annotation>
</rdf:RDF>"""

        newIdentifier = 'urn:some:form:of:identifier'
        self.deanonymize._urnGen = lambda: newIdentifier
        lico(self.dna.all.process(lxmlNode=parse(StringIO(xml % ""))))
        self.assertEquals(1, len(self.observer.calledMethods))
        self.assertEqualsWS(xml % ' rdf:about="%s"' % newIdentifier, tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))

