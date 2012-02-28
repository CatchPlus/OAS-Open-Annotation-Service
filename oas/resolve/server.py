from lxml.etree import parse, tostring, Element
from StringIO import StringIO
from urllib2 import urlopen
from urllib import urlencode, unquote
from os.path import join

from weightless.core import be, compose
from meresco.core import Observable
from meresco.components import readConfig, StorageComponent, XmlPrintLxml

from oas.namespaces import xpath, getAttrib, namespaces

from oas.utils.annotation import filterAnnotations, filterFoafAgents, filterOacBodies

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
            items = []
            yield {
                'record': tostring(node),
                'items': [
                    {'filter': filterFoafAgents, 'partname': 'foafAgent', 'urls': xpath(node, "oac:Annotation/dcterms:creator/@rdf:resource")},
                    {'filter': filterOacBodies, 'partname': 'oacBody', 'urls': xpath(node, "oac:Annotation/oac:hasBody/@rdf:resource")},
                ]
            }

    def _urlopen(self, url):
        return urlopen(url)
    
    def process(self):
        for resolvable in self.listResolvables():
            items = resolvable['items']
            for item in items:
                for url in item['urls']:
                    try:
                        lxmlNode = parse(self._urlopen(url))
                    except:
                        print "Error retrieving", url
                        continue
                    for node in item['filter'](lxmlNode):
                        identifier = getAttrib(node, "rdf:about")
                        newNode = parse(StringIO(tostring(node)))
                        yield self.all.add(identifier=identifier, partname=item['partname'], lxmlNode=newNode)
                self.call.inject(resolvable['record'])
             
class RecordInject(object):
    def __init__(self, injectUrl):
        self._injectUrl = injectUrl

    def inject(self, xml):
        print urlopen(self._injectUrl, xml).read()

def dna(config):
    baseurl = "http://%(hostName)s:%(portNumber)s/sru" % config
    injectUrl = "http://%(hostName)s:%(portNumber)s/inject" % config
    databasePath = config['databasePath']
    storage = StorageComponent(join(databasePath, 'storage'))

    return \
        (Observable(),
            (ResolveServer(),
                (SruClient(baseurl=baseurl),),
                (XmlPrintLxml(fromKwarg='lxmlNode', toKwarg='data'),
                    (storage,),
                ),
                (RecordInject(injectUrl),),
            )
        )


def startServer(configFile):
    config = readConfig(configFile)
    server = be(dna(config))
    list(compose(server.once.observer_init()))
    list(compose(server.all.process()))


