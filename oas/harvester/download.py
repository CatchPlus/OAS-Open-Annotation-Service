from urllib2 import urlopen
from lxml.etree import parse

from meresco.core import Observable

class Download(Observable):
    def __init__(self, host):
        Observable.__init__(self)
        self.host = host

    def process(self):
        request = self.call.buildPathAndArguments()
        lxmlNode = parse(urlopen("%s%s" % (self.host, request)))
        yield self.all.handle(lxmlNode)
