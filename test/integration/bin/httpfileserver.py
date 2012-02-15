#!/usr/bin/env python

from meresco.components.http import FileServer, ObservableHttpServer
from meresco.core import Observable
from weightless.io import Reactor
from weightless.core import be, compose
from sys import argv

def main(reactor, portnumber, filepath):
    return be(
        (Observable(),
            (ObservableHttpServer(reactor, portnumber),
                (FileServer(filepath),)
            )
        )
    )

if __name__ == '__main__':
    args = {}
    for i in range(1, len(argv), 2):
        args[argv[i][2:]] = argv[i+1]
    portnumber = int(args['port'])
    filepath = args['filepath']
    
    reactor = Reactor()
    server = main(reactor, portnumber, filepath)
    list(compose(server.once.observer_init()))
    reactor.loop()

