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
                version="1.2", 
                query=query, 
                operation="searchRetrieve")))
        return parse(StringIO(urlopen(url).read()))

class ResolveServer(Observable):
    def __init__(self, query="__resolved__ = no"):
        Observable.__init__(self)
        self._query = query

    def listResolvables(self):
        response = self.call.searchRetrieve(self._query)

        records = xpath(response, "/srw:searchRetrieveResponse/srw:records/srw:record")
        nodes = xpath(response, "/srw:searchRetrieveResponse/srw:records/srw:record/srw:recordData/rdf:RDF")
        for record in records:
            node = xpath(record, "srw:recordData/rdf:RDF")[0]
            items = []
            yield {
                'identifier': xpath(record, "srw:recordIdentifier/text()")[0],
                'items': [
                    {   'filter': filterFoafAgents, 
                        'partname': 'foafAgent', 
                        'urls': xpath(node, "oac:Annotation/dcterms:creator/@rdf:resource")
                    },
                    {   'filter': filterOacBodies, 
                        'partname': 'oacBody', 
                        'urls': xpath(node, "oac:Annotation/oac:hasBody/@rdf:resource")
                    },
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
                self.call.inject(resolvable['identifier'])
             
class RecordInject(object):
    def __init__(self, injectUrl):
        self._injectUrl = injectUrl

    def inject(self, identifier):
        print urlopen(self._injectUrl + "?%s" % urlencode({'identifier': identifier})).read()

def dna(config):
    baseurl = "http://%(hostName)s:%(portNumber)s/sru" % config
    injectUrl = "http://127.0.0.1:%(portNumber)s/recordReindex" % config
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


