from os.path import join, basename
from sys import stdout

from meresco.core import Observable, be

from meresco.components import readConfig
from meresco.components.http import ObservableHttpServer, StringServer, BasicHttpHandler, PathFilter
from meresco.components.http.utils import ContentTypePlainText

from weightless.io import Reactor
from dynamichtml import DynamicHtml

from oas import VERSION_STRING

dynamicHtmlFilePath = join(basename(__file__), "dynamic")

def dna(reactor, observableHttpServer, config):
   return \
        (Observable(),
            (observableHttpServer,
                (BasicHttpHandler(),
                    (PathFilter("/", excluding=["/info"]),
                        (DynamicHtml([dynamicHtmlFilePath], reactor=reactor, indexPage='/nl/page/body/search'),
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

