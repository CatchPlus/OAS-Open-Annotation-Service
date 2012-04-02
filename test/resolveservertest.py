## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of 
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
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
from StringIO import StringIO
from lxml.etree import tostring, parse
from meresco.core import Observable
from weightless.core import be, compose
from oas.resolve.server import ResolveServer
from oas.utils import filterFoafAgents

class ResolveServerTest(SeecrTestCase):
    def testOne(self):
        server = ResolveServer()
        observer = CallTrace(emptyGeneratorMethods=['add'])
        dna = be(
            (Observable(),
                (server,
                    (observer,)
                )
            )
        )
        server.listResolvables = lambda: [{'items': [{'filter': filterFoafAgents, 'partname': 'foafAgent', 'urls': ['some:url']}], 'identifier': 'urn:some:identifier'}]
        server._urlopen = lambda url: StringIO("""<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<rdf:Description rdf:about="http://oas.dev.seecr.nl:8000/static/dummy_foaf_agent">
<rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Agent"/>
<foaf:name>Pietje Puk</foaf:name>
<dc:title>Gewillig slachtoffer</dc:title>
</rdf:Description>
</rdf:RDF>""")
        
        list(compose(dna.all.process()))
        addCall, injectCall = observer.calledMethods
        self.assertEqualsWS("""<rdf:Description xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:foaf="http://xmlns.com/foaf/0.1/" xmlns:dc="http://purl.org/dc/elements/1.1/" rdf:about="http://oas.dev.seecr.nl:8000/static/dummy_foaf_agent">
        <rdf:type rdf:resource="http://xmlns.com/foaf/0.1/Agent"/>
        <foaf:name>Pietje Puk</foaf:name>
        <dc:title>Gewillig slachtoffer</dc:title>
        </rdf:Description>""", tostring(addCall.kwargs['lxmlNode']))


    def testListResolvables(self):
        server = ResolveServer()
        observer = CallTrace(
            emptyGeneratorMethods=['add'], 
            returnValues={'searchRetrieve': ListResolvablesTest_SRU})
        dna = be(
            (Observable(),
                (server,
                    (observer,)
                )
            )
        )
        resolvables = list(compose(server.listResolvables()))
        self.assertEquals(1, len(resolvables))
        self.assertEquals("http://oas.dev.seecr.nl/resolve/urn:uuid:5318cf36-1599-4b26-8be9-7f7f673e1a79", resolvables[0]['identifier'])

ListResolvablesTest_SRU = parse(StringIO("""
<srw:searchRetrieveResponse xmlns:srw="http://www.loc.gov/zing/srw/" xmlns:diag="http://www.loc.gov/zing/srw/diagnostic/" xmlns:xcql="http://www.loc.gov/zing/cql/xcql/" xmlns:dc="http://purl.org/dc/elements/1.1/">
<srw:version>1.2</srw:version><srw:numberOfRecords>1</srw:numberOfRecords><srw:records><srw:record><srw:recordSchema>rdf</srw:recordSchema><srw:recordPacking>xml</srw:recordPacking><srw:recordIdentifier>http://oas.dev.seecr.nl/resolve/urn:uuid:5318cf36-1599-4b26-8be9-7f7f673e1a79</srw:recordIdentifier><srw:recordData><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" rdf:about="http://oas.dev.seecr.nl/resolve/urn:uuid:5318cf36-1599-4b26-8be9-7f7f673e1a79">
        <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">This is an annotation</dc:title>
        <dcterms:creator xmlns:dcterms="http://purl.org/dc/terms/" rdf:resource="http://localhost:59007/rdf/testResolve"/>
    </oac:Annotation>
</rdf:RDF>
</srw:recordData></srw:record></srw:records><srw:echoedSearchRetrieveRequest><srw:version>1.2</srw:version><srw:query>__resolved__ = no</srw:query><srw:startRecord>1</srw:startRecord><srw:maximumRecords>10</srw:maximumRecords><srw:recordPacking>xml</srw:recordPacking><srw:recordSchema>rdf</srw:recordSchema></srw:echoedSearchRetrieveRequest></srw:searchRetrieveResponse>"""))

