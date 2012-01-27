from os.path import join, basename, dirname
from sys import stdout
from StringIO import StringIO

from meresco.core import Observable, be, TransactionScope

from meresco.components import readConfig, StorageComponent, Amara2Lxml, XmlPrintLxml, Xml2Fields, Venturi
from meresco.components.http import ObservableHttpServer, StringServer, BasicHttpHandler, PathFilter, PathRename, FileServer
from meresco.components.http.utils import ContentTypePlainText
from meresco.components.sru import SruParser, SruHandler, SRURecordUpdate

from meresco.solr.solrinterface import SolrInterface
from meresco.solr.cql2solrlucenequery import CQL2SolrLuceneQuery
from meresco.solr.fields2solrdoc import Fields2SolrDoc

from uuid import uuid4
from weightless.io import Reactor
from dynamichtml import DynamicHtml

from oas import VERSION_STRING
from namespaces import namespaces, xpath

ALL_FIELD = '__all__'
unqualifiedTermFields = [(ALL_FIELD, 1.0)]

dynamicHtmlFilePath = join(dirname(__file__), "dynamic")
staticHtmlFilePath = join(dirname(__file__), "static")

def dna(reactor, observableHttpServer, config):
    hostName = config['hostName']
    portNumber = int(config['portNumber'])
    databasePath = config['databasePath']
    solrPortNumber = int(config['solrPortNumber'])
    storageComponent = StorageComponent(join(databasePath, 'storage'))

    solrInterface = SolrInterface(host="localhost", port=solrPortNumber, core="oas")

    uploadHelix =  \
        (TransactionScope('batch'),
            (TransactionScope('record'),    
                (Venturi(
                    should=[
                        ('rdf', '/rdf:RDF'),
                    ],
                    namespaceMap=namespaces),

                    (XmlPrintLxml(fromKwarg='lxmlNode', toKwarg='data'),
                        (storageComponent,)
                    ),  
                    (Xml2Fields(),
                        (Fields2SolrDoc(transactionName="record", partname="solr"),
                            (solrInterface,)
                        )   
                    )
                )
            )
        )

    return \
        (Observable(),
            (observableHttpServer,
                (BasicHttpHandler(),
                    (PathFilter("/update"),
                        (SRURecordUpdate(),
                            (Amara2Lxml(fromKwarg="amaraNode", toKwarg="lxmlNode"),
                                uploadHelix,
                            )   
                        )   
                    ),
                    (PathFilter("/", excluding=["/info", "/sru", "/update", "/static"]),
                        (DynamicHtml([dynamicHtmlFilePath], reactor=reactor, 
                            indexPage='/index', 
                            additionalGlobals={
                                'StringIO': StringIO, 
                                'xpath': xpath,
                                'uuid': uuid4,
                                }),
                            uploadHelix
                        )
                    ),
                    (PathFilter('/static'),
                        (PathRename(lambda path: path[len('/static'):]),
                            (FileServer(staticHtmlFilePath),)
                        )
                    ),
                    (PathFilter("/sru"),
                        (SruParser(host=hostName, port=portNumber, 
                            defaultRecordSchema='rdf', defaultRecordPacking='xml'),
                            (SruHandler(drilldownSortedByTermCount=True),
                                (CQL2SolrLuceneQuery(unqualifiedTermFields),
                                    (solrInterface,)
                                ),
                                (storageComponent,),
                            )
                        )

                    ),
                    (PathFilter('/info/version'),
                        (StringServer(VERSION_STRING, ContentTypePlainText),)
                    ),  
                )
            )
        )





def startServer(configFile):
    config = readConfig(configFile)
    hostName = config['hostName']
    portNumber = int(config['portNumber'])
    databasePath = config['databasePath']

    reactor = Reactor()
    observableHttpServer = ObservableHttpServer(reactor, portNumber)

    server = be(dna(reactor, observableHttpServer, config))
    server.once.observer_init()

    print "Server listening on", hostName, "at port", portNumber
    print "   - database:", databasePath, "\n"
    stdout.flush()
    reactor.loop()

