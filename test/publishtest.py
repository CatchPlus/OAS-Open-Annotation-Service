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
from meresco.core import Observable, Transparent

from lxml.etree import parse, tostring
from StringIO import StringIO

from oas import Publish

from testutil import lico

class PublishTest(SeecrTestCase):

    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace(emptyGeneratorMethods=['add'])
        self.store = CallTrace(emptyGeneratorMethods=['add'])
        self.dna = be(
            (Observable(),
                (Publish(baseUrl="http://some.where/here"),
                    (Transparent(name="index"),
                        (self.observer, ),
                    ),
                    (Transparent(name="store"),
                        (self.store, )
                    ),
                )
            )
        )

    def testOne(self):
        xml="""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="urn:id:1"/>
</rdf:RDF>"""
        lico(self.dna.all.process(parse(StringIO(xml))))
        self.assertEqualsWS("""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="http://some.where/here/urn%3Aid%3A1"><dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/">urn:id:1</dc:identifier></oac:Annotation>
</rdf:RDF>""", tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))
        self.assertEquals("http://some.where/here/urn%3Aid%3A1", self.observer.calledMethods[0].kwargs['identifier'])

    def testDontPublishIfAlreadyAnURL(self):
        xml="""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="http://some.where.else/1"/>
</rdf:RDF>"""
        lico(self.dna.all.process(parse(StringIO(xml))))
        self.assertEqualsWS(xml, tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))
        self.assertEquals("http://some.where.else/1", self.observer.calledMethods[0].kwargs['identifier'])

    def testPublishBodyToo(self):
        xml="""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="urn:id:1">
        <oac:hasBody>
            <oac:Body rdf:about="urn:id:2"/>
        </oac:hasBody>
    </oac:Annotation>
</rdf:RDF>"""
        lico(self.dna.all.process(parse(StringIO(xml))))
        self.assertEqualsWS("""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="http://some.where/here/urn%3Aid%3A1">
        <oac:hasBody>
            <oac:Body rdf:about="http://some.where/here/urn%3Aid%3A2">
                <dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/">urn:id:2</dc:identifier>
            </oac:Body>
        </oac:hasBody>
        <dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/">urn:id:1</dc:identifier>
    </oac:Annotation>
</rdf:RDF>""", tostring(self.observer.calledMethods[0].kwargs['lxmlNode']))
        self.assertEquals("http://some.where/here/urn%3Aid%3A2", self.store.calledMethods[0].kwargs['identifier'])
        self.assertEquals("http://some.where/here/urn%3Aid%3A1", self.observer.calledMethods[0].kwargs['identifier'])


    def testPublishChecksForBodyInStorage(self):
        xml="""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="urn:id:1">
        <oac:hasBody rdf:resource="urn:id:2"/>
    </oac:Annotation>
</rdf:RDF>"""
        expectedXml="""<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:oac="http://www.openannotation.org/ns/">
    <oac:Annotation rdf:about="http://some.where/here/urn%3Aid%3A1">
        <oac:hasBody>
            <xml/> 
        </oac:hasBody>
        <dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/">urn:id:1</dc:identifier>
    </oac:Annotation>
</rdf:RDF>"""
        self.store.returnValues['isAvailable'] = (False, False)

        lico(self.dna.all.process(parse(StringIO(xml))))
        self.assertEquals('isAvailable', self.store.calledMethods[0].name)
        self.assertEquals('http://some.where/here/urn%3Aid%3A2', self.store.calledMethods[0].args[0])
        self.assertEquals('oacBody', self.store.calledMethods[0].args[1])
        self.assertEquals(1, len(self.store.calledMethods))


        self.store.returnValues['isAvailable'] = (True, True)
        self.store.returnValues['getStream'] = StringIO('<xml/>')
        lico(self.dna.all.process(parse(StringIO(xml))))

        self.assertEquals('getStream', self.store.calledMethods[2].name)
        self.assertEquals(('http://some.where/here/urn%3Aid%3A2', 'oacBody'), self.store.calledMethods[2].args)
    
        self.assertEquals('add', self.observer.calledMethods[1].name)
        self.assertEqualsWS(expectedXml, tostring(self.observer.calledMethods[1].kwargs['lxmlNode']))

