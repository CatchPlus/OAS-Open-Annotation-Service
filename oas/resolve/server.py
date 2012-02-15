from lxml.etree import parse, tostring
from StringIO import StringIO
from urllib2 import urlopen
from urllib import urlencode, unquote
from os.path import join

from weightless.core import be, compose
from meresco.core import Observable
from meresco.components import readConfig, StorageComponent, XmlPrintLxml

from oas.namespaces import xpath, getAttrib
from oas.utils.annotation import filterAnnotations, filterFoafAgents

class SruClient(object):
    def __init__(self, baseurl):
        self._baseurl = baseurl

    def searchRetrieve(self, query):
        url = "%s?%s" % (
            self._baseurl, 
            urlencode(dict(
                version="1.1", 
                query=query, 
                operation="searchRetrieve")))
        return parse(StringIO(urlopen(url).read()))

class ResolveServer(Observable):
    def __init__(self, query="__resolved__ = no"):
        Observable.__init__(self)
        self._query = query

    def listResolvables(self):
        response = self.call.searchRetrieve(self._query)
        nodes = xpath(response, "/srw:searchRetrieveResponse/srw:records/srw:record/srw:recordData/rdf:RDF")
        for node in nodes:
            yield {
                'record': tostring(node),
                'creator_urls': xpath(node, "oac:Annotation/dcterms:creator/@rdf:resource")
            }

    def process(self):
        for resolvable in self.listResolvables():
            urls = resolvable['creator_urls']
            for url in urls:
                lxmlNode = parse(urlopen(url))
                for agent in filterFoafAgents([lxmlNode]):
                    identifier = getAttrib(agent, "rdf:about")
                    yield self.all.add(identifier=identifier, partname="rdf", lxmlNode=lxmlNode)
            self.call.inject(resolvable['record'])
             
class RecordInject(object):
    def __init__(self, injectUrl):
        self._injectUrl = injectUrl

    def inject(self, xml):
        #print "---", xml
        print urlopen(self._injectUrl, xml).read()

def dna(config):
    baseurl = "http://%(hostName)s:%(portNumber)s/sru" % config
    injectUrl = "http://%(hostName)s:%(portNumber)s/inject" % config
    databasePath = config['databasePath']
    foafAgentStorage = StorageComponent(join(databasePath, 'foafAgent'))

    return \
        (Observable(),
            (ResolveServer(),
                (SruClient(baseurl=baseurl),),
                (XmlPrintLxml(fromKwarg='lxmlNode', toKwarg='data'),
                    (foafAgentStorage,),
                ),
                (RecordInject(injectUrl),),
            )
        )


def startServer(configFile):
    config = readConfig(configFile)
    server = be(dna(config))
    list(compose(server.once.observer_init()))
    list(compose(server.all.process()))


