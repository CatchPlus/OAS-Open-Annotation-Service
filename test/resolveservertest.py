from seecr.test import SeecrTestCase, CallTrace
from StringIO import StringIO
from lxml.etree import tostring
from meresco.core import Observable
from weightless.core import be, compose
from oas.resolve.server import ResolveServer

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
        server.listResolvables = lambda: [{'creator_urls': ['some:url'], 'record': '<xml/>'}]
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
