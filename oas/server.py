from os.path import join, basename, dirname, splitext
from os import listdir
from sys import stdout
from StringIO import StringIO
from uuid import uuid4
from urllib import unquote_plus

from weightless.core import compose, be
from weightless.io import Reactor

from meresco.core import Observable, TransactionScope, Transparent

from meresco.components import readConfig, StorageComponent, Amara2Lxml, XmlPrintLxml, Xml2Fields, Venturi, RenameField, XPath2Field, Reindex, FilterMessages, TransformFieldValue, CQLConversion, RenameCqlIndex, FilterField, XmlXPath, RewritePartname
from meresco.components.http import ObservableHttpServer, StringServer, BasicHttpHandler, PathFilter, PathRename, FileServer, ApacheLogger
from meresco.components.http.utils import ContentTypePlainText, okXml
from meresco.components.sru import SruParser, SruHandler, SRURecordUpdate

from meresco.solr.solrinterface import SolrInterface
from meresco.solr.cql2solrlucenequery import CQL2SolrLuceneQuery
from meresco.solr.fields2solrdoc import Fields2SolrDoc

from meresco.owlim import HttpClient

from meresco.oai import OaiPmh, OaiJazz, OaiAddRecord

from dynamichtml import DynamicHtml

from oas import VERSION_STRING
from oas import FilterFieldValue
from oas.seecroaiwatermark import SeecrOaiWatermark
from oas.identifierfromxpath import IdentifierFromXPath
from oas import Sanitize
from namespaces import namespaces, xpath

ALL_FIELD = '__all__'
unqualifiedTermFields = [(ALL_FIELD, 1.0)]

dynamicHtmlFilePath = join(dirname(__file__), "dynamic")
staticHtmlFilePath = join(dirname(__file__), "static")
planninggameFilePath = join(dirname(dirname(__file__)), "doc", "planninggame")

untokenized = [
    "dcterms:creator",
    "oac:hasBody",
    "oac:hasTarget"
]

def fieldnameLookup(name):
    return 'untokenized.'+name if name in untokenized else name

class PrintFieldlet(Observable):
    def addField(self, name, value):
        print "--->", name, value
        self.do.addField(name, value)

def dna(reactor, observableHttpServer, config):
    hostName = config['hostName']
    portNumber = int(config['portNumber'])
    databasePath = config['databasePath']
    solrPortNumber = int(config['solrPortNumber'])
    storageComponent = StorageComponent(join(databasePath, 'storage'))
    publicDocumentationPath = config['publicDocumentationPath']


    reindexPath = join(databasePath, 'reindex')

    solrInterface = SolrInterface(host="localhost", port=solrPortNumber, core="oas")

    tripleStore = HttpClient(host="localhost", port=int(config['owlimPortNumber']))

    oaiJazz = OaiJazz(join(databasePath, 'oai'))

    indexHelix = \
        (Fields2SolrDoc(transactionName="record", partname="solr"),
            (solrInterface,)
        )   
    allFieldIndexHelix = \
        (RenameField(lambda name: "__all__"),
            indexHelix
        )

    indexWithoutFragment = \
        (FilterFieldValue(lambda value: value.startswith('http') and '#' in value),
            (TransformFieldValue(lambda value: value.split('#', 1)[0]),
                indexHelix,
                allFieldIndexHelix,
            )
        )

    uploadHelix =  \
        (TransactionScope('record'),    
            (Venturi(
                    should=[dict(partname='rdf', xpath='/rdf:RDF'),],
                    namespaceMap=namespaces
                ),
                (FilterMessages(allowed=['getStream', 'isAvailable']),
                    (storageComponent,),
                ),
                (OaiAddRecord(),
                    (oaiJazz, )
                ),
                (XmlPrintLxml(fromKwarg='lxmlNode', toKwarg='data'),
                    (storageComponent,),
                    (tripleStore,),
                ),  
                (XmlXPath(["/rdf:RDF/oac:Annotation/dcterms:creator/foaf:Agent[@rdf:about]"], fromKwarg="lxmlNode", namespaceMap=namespaces),
                    (IdentifierFromXPath('@rdf:about'),
                        (RewritePartname('foafAgent'),
                            (XmlPrintLxml(fromKwarg='lxmlNode', toKwarg='data'),
                                (storageComponent, )
                            )
                        )
                    )
                ),
                (XPath2Field([
                    ("/rdf:RDF/oac:Annotation/dc:title/text()", 'dc:title'),
                    ("/rdf:RDF/oac:Annotation/dcterms:created/text()", 'dcterms:created'),
                    ], namespaceMap=namespaces),
                    indexHelix
                ),
                (XPath2Field([
                    ("/rdf:RDF/oac:Annotation/dcterms:creator/@rdf:resource", 'dcterms:creator'),
                    ("/rdf:RDF/oac:Annotation/oac:hasBody/@rdf:resource", 'oac:hasBody'),
                    ("/rdf:RDF/oac:Annotation/oac:hasTarget/@rdf:resource", 'oac:hasTarget'),
                    ("//foaf:mbox/@rdf:resource", '__all__'),

                    ], namespaceMap=namespaces),
                    
                    (FilterField(lambda name: name in untokenized), 
                        (RenameField(lambda name: 'untokenized.'+name),
                            indexWithoutFragment,
                            indexHelix
                        )
                    ),
                    # oac:hasBody, dcterms:creators that have an url need to be resolved. 
                    # This is done Offline, therefore we mark the record.
                    (FilterField(lambda name: name in ['dcterms:creator', 'oac:hasBody']),
                        (FilterFieldValue(lambda value: value.startswith('http://')),
                            (RenameField(lambda name: '__resolved__'),
                                (TransformFieldValue(lambda value: 'no'),
                                    indexHelix
                                )
                            )
                        )
                    ),
                    allFieldIndexHelix,
                    indexHelix
                ),
                (Xml2Fields(),
                    allFieldIndexHelix,
                    indexHelix
                )
            )
        )

    sanitizeAndUploadHelix = \
        (Sanitize(resolveBaseUrl=config['resolveBaseUrl']),
            (FilterMessages(allowed=['isAvailable', 'getStream']),
                (storageComponent,)
            ),
            uploadHelix,
        )

    return \
        (Observable(),
            (observableHttpServer,
                (BasicHttpHandler(),
                    (ApacheLogger(stdout),
                        (PathFilter("/update"),
                            (SRURecordUpdate(),
                                (Amara2Lxml(fromKwarg="amaraNode", toKwarg="lxmlNode"),
                                    sanitizeAndUploadHelix,
                                )   
                            )   
                        ),
                        (PathFilter("/reindex"),
                            (Reindex(partName="rdf", filelistPath=reindexPath),
                                (FilterMessages(allowed=["listIdentifiers"]),
                                    (storageComponent,),
                                ),
                                uploadHelix
                                #sanitizeAndUploadHelix
                            )
                        ),
                        (PathFilter("/", excluding=["/info", "/sru", "/update", "/static", "/oai", "/planninggame", "/reindex", '/public']),
                            (DynamicHtml([dynamicHtmlFilePath], reactor=reactor, 
                                indexPage='/index', 
                                additionalGlobals={
                                    'listDocs': lambda: sorted([name for name in listdir(publicDocumentationPath) if not name.startswith('.')]),
                                    'okXml': okXml,
                                    'splitext': splitext,
                                    'StringIO': StringIO, 
                                    'unquote_plus': unquote_plus,
                                    'uuid': uuid4,
                                    'xpath': xpath,
                                    'config': config,
                                    }),
                                (FilterMessages(allowed=['getStream']),
                                    (storageComponent,),
                                ),
                                sanitizeAndUploadHelix,
                                (FilterMessages(disallowed=['add', 'delete']),
                                    (tripleStore,),
                                ),
                            )
                        ),
                        (PathFilter('/static'),
                            (PathRename(lambda path: path[len('/static'):]),
                                (FileServer(staticHtmlFilePath),)
                            )
                        ),
                        (PathFilter('/public'),
                            (PathRename(lambda path: path[len('/public'):]),
                                (FileServer(publicDocumentationPath),)
                            )
                        ),
                        (PathFilter("/sru"),
                            (SruParser(host=hostName, port=portNumber, 
                                defaultRecordSchema='rdf', defaultRecordPacking='xml'),
                                (SruHandler(drilldownSortedByTermCount=True),
                                    (CQLConversion(RenameCqlIndex(fieldnameLookup), fromKwarg='cqlAbstractSyntaxTree'),
                                        (CQL2SolrLuceneQuery(unqualifiedTermFields),
                                            (solrInterface,)
                                        ),
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
                        (PathFilter('/planninggame'),
                            (PathRename(lambda path: path[len('/planninggame'):]),
                                (FileServer(planninggameFilePath),)
                            )
                        )
                    )
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
    list(compose(server.once.observer_init()))

    print "Server listening on", hostName, "at port", portNumber
    print "   - database:", databasePath, "\n"
    stdout.flush()
    reactor.loop()

