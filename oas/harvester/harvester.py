from environment import Environment

from os.path import join
from urlparse import urlsplit
from urllib2 import urlopen
from lxml.etree import parse

from meresco.oai import OaiDownloadProcessor
from meresco.core import Observable
from weightless.core import compose, be

from oas.namespaces import xpath

class Download(Observable):
    def __init__(self, host):
        Observable.__init__(self)
        self.host = host

    def process(self):
        request = self.call.buildPathAndArguments()
        lxmlNode = parse(urlopen("%s%s" % (self.host, request)))
        yield self.all.handle(lxmlNode)


from socket import socket
from lxml.etree import parse, tostring
from xml.sax.saxutils import escape as xmlEscape

class SruUpload(object):
    def __init__(self, hostname='localhost', portnumber=8000, path='/update', apiKey=''):
        self.hostname = hostname
        self.portnumber = portnumber
        self.path = path
        self.apiKey = apiKey

    def delete(self, identifier):
        body = """<ucp:updateRequest xmlns:ucp="info:lc/xmlns/update-v1">
            <srw:version xmlns:srw="http://www.loc.gov/zing/srw/">1.0</srw:version>
            <ucp:action>info:srw/action/1/delete</ucp:action>
            <ucp:recordIdentifier>%s</ucp:recordIdentifier>
        </ucp:updateRequest>""" % xmlEscape(identifier)
        return self._send(body)


    def upload(self, lxmlNode):
        # construct the body, insert the identifier and supplied XML.
        body = """<ucp:updateRequest xmlns:ucp="info:lc/xmlns/update-v1">
            <srw:version xmlns:srw="http://www.loc.gov/zing/srw/">1.0</srw:version>
            <ucp:action>info:srw/action/1/replace</ucp:action>
            <ucp:recordIdentifier>IGNORED</ucp:recordIdentifier>
            <srw:record xmlns:srw="http://www.loc.gov/zing/srw/">
                <srw:recordPacking>xml</srw:recordPacking>
                <srw:recordSchema>rdf</srw:recordSchema>
                <srw:recordData>%s</srw:recordData>
            </srw:record>
        </ucp:updateRequest>""" % tostring(lxmlNode)
        return self._send(body)

    def _send(self, body):
         # Connect to the server and send the update request.
        s = socket()
        s.connect((self.hostname, self.portnumber))
        s.send("POST %s HTTP/1.0\r\n" % self.path)
        s.send("Content-Type: text/xml\r\n")
        s.send("Content-Length: %s\r\n" % len(body))
        s.send("Authorization: %s\r\n" % self.apiKey)
        s.send("\r\n")
        s.sendall(body)

        # Receive the answer from the server and print it to stdout.
        response = s.recv(1024)
        while True:
            part = s.recv(1024)
            if part == "":
                break
            response += part
        s.close()
        return response

    def add(self, identifier, lxmlNode, datestamp):
        if xpath(lxmlNode, "/oai:record/oai:header[@status='deleted']"):
            response = self.delete(identifier=''.join(xpath(lxmlNode, "/oai:record/oai:header/oai:identifier/text()")))
        else:
            for record in xpath(lxmlNode, "/oai:record/oai:metadata/*"):
                response = self.upload(lxmlNode=record)
        print 'SRU update response', response
        return
        yield

def main(config):
    env = Environment(root=join(config['databasePath'], 'harvester'))
    for repository in env.getRepositories():
        scheme, netloc, path, _, _ = urlsplit(repository.baseUrl)
        dna = be(
            (Observable(),
                (Download(host='%s://%s' % (scheme, netloc)),
                    (OaiDownloadProcessor(
                            path=path, 
                            metadataPrefix=repository.metadataPrefix,
                            set=repository.setSpec,
                            workingDirectory=repository.directory,
                            err=open(repository.errorLogPath, 'a'),
                            xWait=False),
                        (SruUpload(hostname=config['hostName'], portnumber=config['portNumber'], path=config['sru.updatePath'], apiKey=repository.apiKey),)
                    )
                )
            )
        )
        list(compose(dna.all.process()))

