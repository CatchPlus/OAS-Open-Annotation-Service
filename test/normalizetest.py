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

from testutil import lico

from oas import Normalize
from oas.normalize import splitType

class NormalizeTest(SeecrTestCase):

    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace(emptyGeneratorMethods=['process', "delete"])
        self.dna = be(
            (Observable(),
                (Normalize(),
                    (self.observer,)
                )
            )
        )
   
    def assertConvert(self, expected, source):
        lico(self.dna.all.process(lxmlNode=parse(StringIO(source))))

        resultNode = self.observer.calledMethods[0].kwargs['lxmlNode']
        self.assertEqualsWS(
            expected, 
            tostring(resultNode, pretty_print=True))


    def testOne(self):
        XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about="urn:identifier">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
    </rdf:Description>
</rdf:RDF>"""
        EXPECTED_XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" rdf:about="urn:identifier"/>
</rdf:RDF>"""
        self.assertConvert(EXPECTED_XML, XML)

    def testSubElements(self):
        XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
    <rdf:Description rdf:about="urn:identifier">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
        <dc:title>A title</dc:title>
    </rdf:Description>
</rdf:RDF>"""
        EXPECTED_XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dc="http://purl.org/dc/elements/1.1/">
    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" rdf:about="urn:identifier">
        <dc:title>A title</dc:title>
    </oac:Annotation>
</rdf:RDF>"""
        self.assertConvert(EXPECTED_XML, XML)

    def testMultiple(self):
        XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/">
    <rdf:Description rdf:about="urn:identifier">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
        <dcterms:creator>
            <rdf:Description rdf:about="urn:agent">
                <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Agent"/>
            </rdf:Description>
        </dcterms:creator>
    </rdf:Description>
</rdf:RDF>"""
        EXPECTED_XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/">
    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" rdf:about="urn:identifier">
        <dcterms:creator>
            <foaf:Agent xmlns:foaf="http://xmlns.com/foaf/0.1/" rdf:about="urn:agent"/>
        </dcterms:creator>
    </oac:Annotation>
</rdf:RDF>"""
        self.assertConvert(EXPECTED_XML, XML)
    
    def testMultipleRdfTypes(self):
        XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/">
    <rdf:Description rdf:about="urn:identifier">
        <rdf:type rdf:resource="http://www.openannotation.org/ns/Annotation"/>
        <rdf:type rdf:resource="http://www.example.org/lit-annotation-ns#ExplanatoryNote"/>
    </rdf:Description>
</rdf:RDF>"""
        EXPECTED_XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/">
    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" rdf:about="urn:identifier">
        <rdf:type rdf:resource="http://www.example.org/lit-annotation-ns#ExplanatoryNote"/>
    </oac:Annotation>
</rdf:RDF>"""
        self.assertConvert(EXPECTED_XML, XML)
    def testLeaveDescriptionsWithoutTypeAlone(self):
        XML = """<rdf:RDF 
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/">
    <rdf:Description rdf:about="urn:identifier">
        <dcterms:creator>
            <rdf:Description rdf:about="urn:agent"/>
        </dcterms:creator>
    </rdf:Description>
</rdf:RDF>"""
        self.assertConvert(XML, XML)

    def testSplitRdfType(self):
        self.assertEquals(("http://ns/", "Type"), splitType("http://ns/Type")) 
        self.assertEquals(("http://ns#", "Type"), splitType("http://ns#Type")) 

    def testDeletePassedOn(self):
        lico(self.dna.all.delete(
            identifier='identifier', 
            partname='rdf', 
            lxmlNode=parse(StringIO("<xml/>"))))

        self.assertEquals(['delete'], [m.name for m in self.observer.calledMethods])
