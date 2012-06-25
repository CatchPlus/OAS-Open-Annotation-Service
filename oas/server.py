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

from os.path import join, basename, dirname, splitext
from os import listdir
from sys import stdout
from StringIO import StringIO
from uuid import uuid4
from urllib import unquote_plus
from time import strftime, localtime
from xml.sax.saxutils import quoteattr

from weightless.core import compose, be
from weightless.io import Reactor

from meresco.core import Observable, TransactionScope, Transparent

from meresco.components import readConfig, StorageComponent, Amara2Lxml, XmlPrintLxml, Xml2Fields, Venturi, RenameField, XPath2Field, Reindex, FilterMessages, TransformFieldValue, CQLConversion, RenameCqlIndex, FilterField, XmlXPath, RewritePartname, FilterPartByName
from meresco.components.http import ObservableHttpServer, StringServer, BasicHttpHandler, PathFilter, PathRename, FileServer, ApacheLogger, SessionHandler, IpFilter
from meresco.components.http.utils import ContentTypePlainText, okXml
from meresco.components.sru import SruParser, SruHandler, SRURecordUpdate

from meresco.solr.solrinterface import SolrInterface
from meresco.solr.cql2solrlucenequery import CQL2SolrLuceneQuery
from meresco.solr.fields2solrdoc import Fields2SolrDoc

from meresco.owlim import HttpClient

from meresco.oai import OaiPmh, OaiJazz, OaiAddRecord

from dynamichtml import DynamicHtml
from namespaces import namespaces, xpath
from oas.adduserdatafromapikey import AddUserDataFromApiKey
from oas.apikeycheck import ApiKeyCheck
from oas.apikey import ApiKey
from oas.datatofield import DataToField
from oas.identifierfromxpath import IdentifierFromXPath
from oas import Authorization, ReindexIdentifier, OaiUserSet
from oas import FilterFieldValue
from oas import RdfTypeToField
from oas import MultipleAnnotationSplit, Normalize, Deanonymize, Publish
from oas import VERSION_STRING
from oas.login import BasicHtmlLoginForm, createPasswordFile
from oas.seecroaiwatermark import SeecrOaiWatermark
from oas.userdelete import UserDelete
from oas.harvester import Dashboard, Environment

ALL_FIELD = '__all__'
unqualifiedTermFields = [(ALL_FIELD, 1.0)]

dynamicHtmlFilePath = join(dirname(__file__), "dynamic")
staticHtmlFilePath = join(dirname(__file__), "static")
planninggameFilePath = join(dirname(dirname(__file__)), "doc", "planninggame")

untokenized = [
        #"dcterms:creator",
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
    sruUpdatePath = config['sru.updatePath']
    solrPortNumber = int(config['solrPortNumber'])
    storageComponent = StorageComponent(join(databasePath, 'storage'), partsRemovedOnDelete=['rdf', 'user'])
    publicDocumentationPath = config['publicDocumentationPath']
    passwordFile = createPasswordFile(filename=join(databasePath, 'passwd'), salt='jasdf89pya')
    apiKey = ApiKey(join(databasePath, 'apikeys'))

    reindexPath = join(databasePath, 'reindex')
    harvesterDashboardPath = join(databasePath, 'harvester')

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

    apiKeyHelix = (apiKey,
        (passwordFile,),
    )

    basicHtmlLoginHelix = (BasicHtmlLoginForm(action="/login.action", loginPath="/login"),
        (passwordFile,),
        apiKeyHelix,
        (UserDelete(join(databasePath, 'userdelete')),),
    )

    harvesterEnv = Environment(root=harvesterDashboardPath)
    harvesterDashboardHelix = \
        (Dashboard(), 
            (harvesterEnv, )
        )

    readOnlyStorageHelix = \
        (FilterMessages(allowed=['getStream', 'isAvailable']),
            (storageComponent,),
        )

    uploadHelix =  \
        (TransactionScope('record'),    
            (Venturi(
                    should=[
                        dict(partname='user', xpath='/ignored', asString=True),
                        dict(partname='rdf', xpath='/rdf:RDF'),
                    ],
                    namespaceMap=namespaces
                ),
                (FilterMessages(allowed=['delete']),
                    (solrInterface, ), 
                    (storageComponent,),
                    (oaiJazz, ),
                    (tripleStore, )
                ),
                readOnlyStorageHelix,
                (FilterPartByName(included=['rdf']),
                    (OaiAddRecord(),
                        (FilterMessages(allowed=["getAllMetadataFormats"]),
                            (oaiJazz, )
                        ),
                        (OaiUserSet(),
                            readOnlyStorageHelix,
                            (oaiJazz, )
                        )
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
                        ("/rdf:RDF/oac:Annotation/oac:hasTarget/*/@rdf:about", 'oac:hasTarget'),
                        ("//oac:constrains/@rdf:resource", 'oac:hasTarget'),
                        ("//foaf:mbox/@rdf:resource", '__all__'),

                        ], namespaceMap=namespaces),
                       
                        (FilterField(lambda name: name == "dcterms:creator"),
                            indexWithoutFragment
                        ),
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
                    (RdfTypeToField(),
                        allFieldIndexHelix,
                        indexHelix
                    ),
                    (Xml2Fields(),
                        (FilterField(lambda name: name.startswith('RDF.Annotation.creator')),
                            (RenameField(lambda name: 'dcterms:creator'),
                                indexHelix
                            )
                        ),
                        (FilterField(lambda name: name.startswith('RDF.Annotation.hasBody.')),
                            (RenameField(lambda name: 'body'),
                                indexHelix
                            )
                        ),
                        allFieldIndexHelix,
                        indexHelix
                    )
                ),
                (FilterPartByName(included=['user']),
                    (DataToField(fromKwarg='data', fieldname='api.user'),
                        allFieldIndexHelix,
                        indexHelix,
                    )
                )
            )
        )

    sanitizeAndUploadHelix = \
        (MultipleAnnotationSplit(),
            readOnlyStorageHelix,
            (Normalize(),
                (Deanonymize(),
                    (Publish(baseUrl=config['resolveBaseUrl']),
                        (Transparent(name="index"),
                            (AddUserDataFromApiKey(),
                                apiKeyHelix,
                                (storageComponent,)
                            ),
                            uploadHelix
                        ),
                        (Transparent(name="store"),
                            (XmlPrintLxml(fromKwarg='lxmlNode', toKwarg='data'),
                                (storageComponent, ),
                            )
                        )
                    )
                )
            )
        )
    sanitizeAndUploadHelixUnchecked = \
        (MultipleAnnotationSplit(),
            readOnlyStorageHelix,
            (Normalize(),
                (Deanonymize(),
                    (Publish(baseUrl=config['resolveBaseUrl']),
                        (Transparent(name="index"),
                            uploadHelix
                        ),
                        (Transparent(name="store"),
                            (XmlPrintLxml(fromKwarg='lxmlNode', toKwarg='data'),
                                (storageComponent, ),
                            )
                        )
                    )
                )
            )
        )

    return \
        (Observable(),
            (observableHttpServer,
                (BasicHttpHandler(),
                    (Authorization(), 
                        (ApacheLogger(stdout),
                            (PathFilter(sruUpdatePath),
                                (ApiKeyCheck(),
                                    (FilterMessages(allowed=['getForApiKey']),
                                        apiKeyHelix,
                                    ),
                                    (SRURecordUpdate(),
                                        (Amara2Lxml(fromKwarg="amaraNode", toKwarg="lxmlNode"),
                                            sanitizeAndUploadHelix,
                                        )   
                                    )   
                                )
                            ),
                            (PathFilter("/reindex"),
                                (Reindex(partName="rdf", filelistPath=reindexPath),
                                    (FilterMessages(allowed=["listIdentifiers"]),
                                        (storageComponent,),
                                    ),
                                    uploadHelix
                                )
                            ),
                            (IpFilter(allowedIps=['127.0.0.1']),
                                (PathFilter("/recordReindex"),
                                    (ReindexIdentifier(),
                                        readOnlyStorageHelix,
                                        sanitizeAndUploadHelixUnchecked,
                                    )
                                ),
                            ),
                            (IpFilter(allowedIps=['127.0.0.1']),
                                (PathFilter("/internal/update"),
                                    (SRURecordUpdate(),
                                        (Amara2Lxml(fromKwarg="amaraNode", toKwarg="lxmlNode"),
                                            uploadHelix
                                        )
                                    )
                                ),
                            ),
                            (SessionHandler(secretSeed='secret :-)'),
                                (PathFilter("/login.action"),
                                    basicHtmlLoginHelix,
                                ),
                                (PathFilter("/apikey.action"),
                                    apiKeyHelix,
                                ),
                                (PathFilter("/harvester.action"),
                                    harvesterDashboardHelix,
                                ),
                                (PathFilter("/", excluding=["/info", "/sru", sruUpdatePath, "/static", "/oai", "/planninggame", "/reindex", '/public', "/login.action", '/apikey.action', "/recordReindex", "/internal/update", "/harvester.action"]),
                                    (DynamicHtml([dynamicHtmlFilePath], reactor=reactor, 
                                        indexPage='/index', 
                                        additionalGlobals={
                                            'config': config,
                                            'formatTimestamp': lambda format: strftime(format, localtime()),
                                            'join': join,
                                            'listDocs': lambda: sorted([name for name in listdir(publicDocumentationPath) if not name.startswith('.')]),
                                            'okXml': okXml,
                                            'quoteattr': quoteattr,
                                            'splitext': splitext,
                                            'StringIO': StringIO, 
                                            'unquote_plus': unquote_plus,
                                            'uuid': uuid4,
                                            'xpath': xpath,
                                            'humanReadableTime': lambda time: strftime("%Y-%m-%d %H:%M:%S", localtime(time)) if not time is None else '',
                                            }),
                                        basicHtmlLoginHelix,
                                        apiKeyHelix,
                                        readOnlyStorageHelix,
                                        (harvesterEnv, ),
                                        (ApiKeyCheck(),
                                            (FilterMessages(allowed=['getForApiKey']),
                                                apiKeyHelix,
                                            ),
                                            sanitizeAndUploadHelix,
                                        ),
                                        (FilterMessages(disallowed=['add', 'delete']),
                                            (tripleStore,),
                                        ),
                                    ),
                                ),
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

