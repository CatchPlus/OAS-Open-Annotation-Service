from environment import Environment

from os.path import join
from urlparse import urlsplit
from lxml.etree import parse

from meresco.oai import OaiDownloadProcessor
from meresco.core import Observable
from weightless.core import compose, be

from oas.harvester import Download, SruUpload

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
                        (SruUpload(
                                hostname=config['hostName'], 
                                portnumber=config['portNumber'], 
                                path=config['sru.updatePath'], 
                                apiKey=repository.apiKey),)
                    )
                )
            )
        )
        list(compose(dna.all.process()))

