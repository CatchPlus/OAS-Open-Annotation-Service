# -*- encoding: utf-8 -*-
## begin license ##
# 
# "Open Annotation Service" enables exchange, storage and search of 
# heterogeneous annotations using a uniform format (Open Annotation format) and
# a uniform web service interface. 
# 
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

from os.path import isdir, join, abspath, dirname, basename
from os import system, listdir, makedirs
from sys import stdout
from hashlib import md5
from random import randint, choice
from time import sleep, time 
from shutil import copy as filecopy
from StringIO import StringIO
from subprocess import Popen
from signal import SIGTERM
from os import waitpid, kill, WNOHANG
from urllib import urlopen, urlencode
from re import DOTALL, compile
from traceback import print_exc
from lxml.etree import XMLSyntaxError, parse

from seecr.test import SeecrTestCase
from meresco.components import readConfig

from utils import getRequest, postRequest, postMultipartForm 


mydir = dirname(abspath(__file__))
projectDir = dirname(dirname(mydir))
binDir = join(projectDir, 'bin')
if not isdir(binDir):
    binDir = '/usr/bin'
documentationDir = join(projectDir, 'doc')
defaultSolrDataDir = join(projectDir, 'solr-data')
docExampleScriptPath = join(documentationDir, 'public', 'example_client.py')
myExampleScriptPath = join(mydir, 'example_client.py')
filecopy(docExampleScriptPath, myExampleScriptPath)
from example_client import upload

class IntegrationTestCase(SeecrTestCase):
    _scriptTagRegex = compile("<script[\s>].*?</script>", DOTALL)
    _entities = {
        '&nbsp;': ' ',
        '&ndash;': "&#8211;",
        '&mdash;': "&#8212;",
        '&lsquo;': "‘",
        '&rsquo;': "’",
        '&larr;': "&lt;-",
    }

    def setUp(self):
        SeecrTestCase.setUp(self)
        global state
        self.state = state
        self.sessionId = None

    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return getattr(self.state, name)

    def parseHtmlAsXml(self, body):
        def forceXml(body):
            newBody = body
            for entity, replacement in self._entities.items():
                newBody = newBody.replace(entity, replacement)
            newBody = self._scriptTagRegex.sub('', newBody)
            return newBody
        try: 
            return parse(StringIO(forceXml(body)))
        except XMLSyntaxError:
            print body 
            raise

    def getPage(self, port, path, arguments=None, expectedStatus="200"):
        additionalHeaders = {}
        if self.sessionId:
            additionalHeaders['Cookie'] = 'session=' + self.sessionId
        header, body = getRequest(port, path, arguments, parse=False, additionalHeaders=additionalHeaders)
        self.assertHttpOK(header, body, expectedStatus=expectedStatus)
        return header, body

    def postToPage(self, port, path, data, expectedStatus="302"):
        additionalHeaders = {}
        if self.sessionId:
            additionalHeaders['Cookie'] = 'session=' + self.sessionId
        postBody = urlencode(data, doseq=True)
        header, body = postRequest(port, path, data=postBody, contentType='application/x-www-form-urlencoded', parse=False, additionalHeaders=additionalHeaders)
        self.assertHttpOK(header, body, expectedStatus=expectedStatus)
        return header, body 

    def assertHttpOK(self, header, body, expectedStatus="200"):
        try:
            self.assertSubstring("HTTP/1.0 %s" % expectedStatus, header)
            self.assertNotSubstring("Traceback", header + "\r\n\r\n" + body)
        except AssertionError, e:
            print header, body
            raise

    def assertSubstring(self, value, s):
        if not value in s:
            raise AssertionError("assertSubstring fails: %s must occur in %s" % (value, s))

    def assertNotSubstring(self, value, s):
        if value in s:
            raise AssertionError("assertNotSubstring fails: %s must not occur in %s" % (value, s))



class IntegrationState(object):
    def __init__(self, stateName, fastMode):
        self.stateName = stateName
        self.pids = {}
        self.integrationTempdir = '/tmp/integrationtest-%s' % stateName 
        self.testdataDir = join(dirname(mydir), 'data/integration')
        self.fastMode = fastMode
        if not fastMode:
            system('rm -rf ' + self.integrationTempdir)
            system('mkdir --parents '+ self.integrationTempdir)

    def _startServer(self, serviceName, executable, serviceReadyUrl, cwd=binDir, redirect=True, **kwargs):
        stdoutfile = join(self.integrationTempdir, "stdouterr-%s.log" % serviceName)
        stdouterrlog = open(stdoutfile, 'w')
        args = [executable]
        fileno = stdouterrlog.fileno() if redirect else None
        for k,v in kwargs.items():
            args.append("--%s" % k)
            args.append(str(v))
        serverProcess = Popen(
            executable=executable,
            args=args,
            cwd=cwd,
            stdout=fileno,
            stderr=fileno
        )
        self.pids[serviceName] = serverProcess.pid

        self._stdoutWrite("Starting service '%s', for state '%s' : v" % (serviceName, self.stateName))
        done = False
        while not done:
            try:
                self._stdoutWrite('r')
                sleep(0.1)
                serviceReadyResponse = urlopen(serviceReadyUrl).read()
                done = True
            except IOError:
                if serverProcess.poll() != None:
                    del self.pids[serviceName]
                    exit('Service "%s" died, check "%s"' % (serviceName, stdoutfile))
        self._stdoutWrite('oom!\n')

    def _stopServer(self, serviceName):
        kill(self.pids[serviceName], SIGTERM)
        waitpid(self.pids[serviceName], WNOHANG)

    def tearDown(self):
        for serviceName in self.pids.keys():
            self._stopServer(serviceName)
    
    @staticmethod
    def _stdoutWrite(aString):
        stdout.write(aString)
        stdout.flush()

class PortNumberGenerator(object):
    startNumber = randint(50000, 60000)

    @classmethod
    def next(cls):
        cls.startNumber += 1
        return cls.startNumber


class OasIntegrationState(IntegrationState):

    def __init__(self, stateName, fastMode):
        IntegrationState.__init__(self, stateName, fastMode)

        self.solrDataDir = join(self.integrationTempdir, "solr")
        self.owlimDataDir = join(self.integrationTempdir, "owlim")
        self.httpDataDir = join(mydir, "httpdata")
        system('mkdir --parents ' + self.solrDataDir)

        if not fastMode:
            system('cp -r %s/* %s' % (defaultSolrDataDir, self.solrDataDir))

        system("sed 's,^jetty\.home=.*$,jetty.home=%s,' -i %s" % (self.solrDataDir, join(self.solrDataDir, 'start.config')))
        self.solrPortNumber = PortNumberGenerator.next()
        self.owlimPortNumber = PortNumberGenerator.next()
        self.portNumber = PortNumberGenerator.next()
        self.httpPortNumber = PortNumberGenerator.next()
        self.hostName = 'localhost'
        
        self.config = config = readConfig(join(documentationDir, 'examples', 'oas.config'))
        self.configFile = join(self.integrationTempdir, 'oas.config')
        
        # test example config has necessary parameters
        def setConfig(config, parameter, value):
            assert config.get(parameter)
            config[parameter] = value

        setConfig(config, 'hostName', self.hostName)
        setConfig(config, 'portNumber', self.portNumber)
        setConfig(config, 'solrPortNumber', self.solrPortNumber)
        setConfig(config, 'owlimPortNumber', self.owlimPortNumber)
        setConfig(config, 'databasePath', join(self.integrationTempdir, 'database'))
        setConfig(config, 'resolveBaseUrl', 'http://localhost:%s/resolve/' % self.portNumber)
        self.publicDocumentationPath = join(documentationDir, 'public')
        setConfig(config, 'publicDocumentationPath', self.publicDocumentationPath)

        with open(self.configFile, 'w') as f:
            for item in config.items():
                f.write('%s = %s\n' % item)

    def initialize(self):
        self._startSolrServer()
        self._startOasServer()
        self._startOwlimServer()
        self._startHttpServer()
        self._createDatabase()
   
    def tearDown(self):
        IntegrationState.tearDown(self)

    def _startOasServer(self):
        self._startServer('oas', join(binDir, 'start-oas-server'), 'http://localhost:%s/info/version' % self.portNumber, configFile=self.configFile)

    def _startSolrServer(self):
        self._startServer('solr', join(binDir, 'start-oas-solr-server'), 'http://localhost:%s/solr/oas/admin/registry.jsp' % self.solrPortNumber, port=self.solrPortNumber, solrDataDir=self.solrDataDir, configFile=self.configFile)

    def _startOwlimServer(self):
        self._startServer('owlim', join(binDir, 'start-oas-owlim-server'), 'http://localhost:%s/sparql' % self.owlimPortNumber, port=self.owlimPortNumber, storeLocation=self.owlimDataDir)

    def _startHttpServer(self):
        self._startServer("http", join(mydir, "bin", "httpfileserver.py"), 'http://localhost:%s/server_ready' % self.httpPortNumber, port=self.httpPortNumber, filepath=self.httpDataDir)

    def _createDatabase(self):
        if fastMode:
            print "Reusing database in", self.integrationTempdir
            return
        recordPacking = 'xml'
        start = time()
        print "Creating database in", self.integrationTempdir
        try:
            if self.stateName in ['default']:
                self._uploadUpdateRequests(self.testdataDir, '/update', [self.portNumber]) 
            elif self.stateName == 'initial':
                pass
            print "Finished creating database in %s seconds" % (time() - start)
        except Exception, e:
            print 'Error received while creating database for', self.stateName
            print_exc()
            exit(1)

    def _uploadUpdateRequests(self, datadir, uploadPath, uploadPorts):
        requests = (join(datadir, r) for r in sorted(listdir(datadir)) if r.endswith('.updateRequest'))
        for filename in requests:
            self._uploadUpdateRequest(filename, uploadPath, uploadPorts)

    def _uploadUpdateRequest(self, filename, uploadPath, uploadPorts):
        aPort = choice(uploadPorts)
        print 'http://localhost:%s%s' % (aPort, uploadPath), '<-', basename(filename)[:-len('.updateRequest')]
        updateRequest = open(filename).read()
        lxml = parse(StringIO(updateRequest))
        header, body = upload(hostname='localhost', portnumber=aPort, path=uploadPath, stream=open(filename)).split('\r\n\r\n', 1)
        if '200 Ok' not in header:
            print 'No 200 Ok response, but:\n', header
            exit(123)
        if "srw:diagnostics" in body:
            print body
            exit(1234)

def globalSetUp(fast, stateName):
    global state, fastMode
    fastMode = fast
    state = OasIntegrationState(stateName, fastMode)
    state.initialize()

def globalTearDown():
    global state
    state.tearDown()

