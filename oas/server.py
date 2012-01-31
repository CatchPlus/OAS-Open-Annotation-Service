from os.path import join, basename, dirname
from sys import stdout
from StringIO import StringIO

from meresco.core import Observable, be, TransactionScope

from meresco.components import readConfig, StorageComponent, Amara2Lxml, XmlPrintLxml, Xml2Fields, Venturi, RenameField, XPath2Field
from meresco.components.http import ObservableHttpServer, StringServer, BasicHttpHandler, PathFilter, PathRename, FileServer
from meresco.components.http.utils import ContentTypePlainText
from meresco.components.sru import SruParser, SruHandler, SRURecordUpdate

from meresco.solr.solrinterface import SolrInterface
from meresco.solr.cql2solrlucenequery import CQL2SolrLuceneQuery
from meresco.solr.fields2solrdoc import Fields2SolrDoc

from meresco.oai import OaiPmh, OaiJazz, OaiAddRecord

from uuid import uuid4
from weightless.io import Reactor
from dynamichtml import DynamicHtml

from oas import VERSION_STRING
from oas import AnnotationFilter
from oas.seecroaiwatermark import SeecrOaiWatermark
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

    oaiJazz = OaiJazz(join(databasePath, 'oai'))

    indexHelix = \
        (Fields2SolrDoc(transactionName="record", partname="solr"),
            (solrInterface,)
        )   


    uploadHelix =  \
        (TransactionScope('batch'),
            (TransactionScope('record'),    
                (Venturi(
                    should=[
                        ('rdf', '/rdf:RDF'),
                    ],
                    namespaceMap=namespaces),
                    (AnnotationFilter(),
                        (OaiAddRecord(),
                            (oaiJazz, )
                        ),
                        (XmlPrintLxml(fromKwarg='lxmlNode', toKwarg='data'),
                            (storageComponent,)
                        ),  
                        (XPath2Field([
                            ("/rdf:RDF/rdf:Description/dc:title/text()", 'dc:title'),
                            ("/rdf:RDF/rdf:Description/dcterms:created/text()", 'dcterms:created'),
                            ("/rdf:RDF/oas:Annotation/dc:title/text()", 'dc:title'),
                            ("/rdf:RDF/oas:Annotation/dcterms:created/text()", 'dcterms:created'),

                            ], namespaceMap=namespaces),
                            indexHelix
                        ),
                        (Xml2Fields(),
                            (RenameField(lambda name: "__all__"),
                                indexHelix
                            ),
                            indexHelix
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
                    (PathFilter("/", excluding=["/info", "/sru", "/update", "/static", "/oai"]),
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
                    (PathFilter('/oai'),
                        (OaiPmh(
                            repositoryName=config['oai.repository.name'],
                            adminEmail=config['oai.admin.email'],
                            repositoryIdentifier=config['oai.repository.identifier']),
                            (storageComponent,),
                            (oaiJazz,),
                            (SeecrOaiWatermark(),),
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

