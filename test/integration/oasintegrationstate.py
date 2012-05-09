# -*- encoding: utf-8 -*-
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

from os.path import isdir, join, abspath, dirname, basename
from os import system, listdir, makedirs
from sys import stdout
from hashlib import md5
from random import randint, choice
from time import sleep, time 
from shutil import copy as filecopy
from StringIO import StringIO
from subprocess import Popen
from urllib import urlopen, urlencode
from traceback import print_exc
from lxml.etree import XMLSyntaxError, parse

from seecr.test import SeecrTestCase
from meresco.components import readConfig

from seecr.test.integrationtestcase import IntegrationState
from seecr.test.utils import getRequest, postRequest, postMultipartForm
from seecr.test.portnumbergenerator import PortNumberGenerator

from oas.utils import parseHeaders
from oas.namespaces import xpath

mydir = dirname(abspath(__file__))
projectDir = dirname(dirname(mydir))
documentationDir = join(projectDir, 'doc')
defaultSolrDataDir = join(documentationDir, 'solr-data')
docExampleScriptPath = join(documentationDir, 'public', 'example_client.py')
myExampleScriptPath = join(mydir, 'example_client.py')
filecopy(docExampleScriptPath, myExampleScriptPath)
from example_client import upload

class OasIntegrationState(IntegrationState):

    def __init__(self, stateName, tests=None, fastMode=False):
        IntegrationState.__init__(self, stateName, tests=tests, fastMode=fastMode)
        self.testdataDir = join(dirname(mydir), 'data/integration')
        self.solrDataDir = join(self.integrationTempdir, "solr")
        self.owlimDataDir = join(self.integrationTempdir, "owlim")
        self.httpDataDir = join(mydir, "httpdata")
        system('mkdir --parents ' + self.solrDataDir)

        if not self.fastMode:
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
        databasePath = join(self.integrationTempdir, 'database')
        self.harvesterDataDir = join(databasePath, 'harvester')
        setConfig(config, 'databasePath', databasePath)
        setConfig(config, 'resolveBaseUrl', 'http://localhost:%s/resolve/' % self.portNumber)
        self.publicDocumentationPath = join(documentationDir, 'public')
        setConfig(config, 'publicDocumentationPath', self.publicDocumentationPath)

        with open(self.configFile, 'w') as f:
            for item in config.items():
                f.write('%s = %s\n' % item)

    def binDir(self, executable=None):
        binDir = join(projectDir, 'bin')
        if not isdir(binDir):
            binDir = '/usr/bin'
        return binDir if executable is None else join(binDir, executable)

    def setUp(self):
        self._startSolrServer()
        self._startOasServer()
        self._startOwlimServer()
        self._startHttpServer()
        self._createDatabase()
   
    def tearDown(self):
        IntegrationState.tearDown(self)

    def runResolveService(self):
        self._runService('resolve', self.binDir('start-oas-resolve-service'), configFile=self.configFile)

    def runUserDeleteService(self):
        self._runService('userdelete', self.binDir('start-oas-userdelete-service'), configFile=self.configFile)

    def _startOasServer(self):
        self._startServer('oas', self.binDir('start-oas-server'), 'http://localhost:%s/info/version' % self.portNumber, configFile=self.configFile)

    def _startSolrServer(self):
        self._startServer('solr', self.binDir('start-oas-solr-server'), 'http://localhost:%s/solr/oas/admin/registry.jsp' % self.solrPortNumber, port=self.solrPortNumber, solrDataDir=self.solrDataDir, configFile=self.configFile)

    def _startOwlimServer(self):
        self._startServer('owlim', self.binDir('start-oas-owlim-server'), 'http://localhost:%s/sparql' % self.owlimPortNumber, port=self.owlimPortNumber, storeLocation=self.owlimDataDir)

    def _startHttpServer(self):
        self._startServer("http", join(mydir, "bin", "httpfileserver.py"), 'http://localhost:%s/server_ready' % self.httpPortNumber, port=self.httpPortNumber, filepath=self.httpDataDir)

    def _setupUsers(self):
        headers, body = postRequest(self.portNumber, '/login.action', urlencode(dict(username="admin", password="admin")), parse=False)
        cookie = parseHeaders(headers)['Set-Cookie']

        headers, body = postRequest(self.portNumber, '/apikey.action/create', urlencode(dict(formUrl='/user_management', username='testUser')), parse=False, additionalHeaders=dict(cookie=cookie))
        headers, body = postRequest(self.portNumber, '/apikey.action/create', urlencode(dict(formUrl='/user_management', username='anotherTestUser')), parse=False, additionalHeaders=dict(cookie=cookie))
        headers, body = postRequest(self.portNumber, '/apikey.action/create', urlencode(dict(formUrl='/user_management', username='postUser')), parse=False, additionalHeaders=dict(cookie=cookie))

        headers, body = getRequest(self.portNumber, '/user_management', additionalHeaders={'Cookie': cookie})
        self.apiKeyForTestUser =  xpath(body, '//div[@id="apiKeys"]/table/tr[form/td[text()="testUser"]]/form/td[@class="apiKey"]/text()')[0]
        assert self.apiKeyForTestUser != None

        self.apiKeyForAnotherTestUser = xpath(body, '//div[@id="apiKeys"]/table/tr[form/td[text()="anotherTestUser"]]/form/td[@class="apiKey"]/text()')[0]
        assert self.apiKeyForAnotherTestUser != None
        
        self.apiKeyForPostUser = xpath(body, '//div[@id="apiKeys"]/table/tr[form/td[text()="postUser"]]/form/td[@class="apiKey"]/text()')[0]
        assert self.apiKeyForPostUser != None

    def _createDatabase(self):
        if self.fastMode:
            print "Reusing database in", self.integrationTempdir
            return
        recordPacking = 'xml'
        start = time()
        self._setupUsers()
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
        for nr, filename in enumerate(requests):
            self._uploadUpdateRequest(nr, filename, uploadPath, uploadPorts)

    def _uploadUpdateRequest(self, nr, filename, uploadPath, uploadPorts):
        aPort = choice(uploadPorts)
        apiKeys = [self.apiKeyForTestUser, self.apiKeyForAnotherTestUser]
        apiKey = apiKeys[nr % len(apiKeys)]
        print 'http://localhost:%s%s' % (aPort, uploadPath), '<-', basename(filename)[:-len('.updateRequest')]
        updateRequest = open(filename).read()
        lxml = parse(StringIO(updateRequest))
        header, body = upload(hostname='localhost', portnumber=aPort, path=uploadPath, stream=open(filename), apiKey=apiKey).split('\r\n\r\n', 1)
        if '200 Ok' not in header:
            print 'No 200 Ok response, but:\n', header
            exit(123)
        if "srw:diagnostics" in body:
            print body
            exit(1234)

    def _runService(self, serviceName, executable, cwd=None, redirect=True, **kwargs):
        stdoutfile = join(self.integrationTempdir, "stdouterr-%s.log" % serviceName)
        serverProcess = self._process(executable, cwd, redirect, stdoutfile, **kwargs)
        self._stdoutWrite("Running service '%s', for state '%s'.\n" % (serviceName, self.stateName))
        result = serverProcess.wait()
        if result:
            exit('Service "%s" exited with %s, check "%s"' % (serviceName, result, stdoutfile))

    def _process(self, executable, cwd, redirect, stdoutfile, **kwargs):
        stdouterrlog = open(stdoutfile, 'w')
        args = [executable]
        fileno = stdouterrlog.fileno() if redirect else None
        for k,v in kwargs.items():
            args.append("--%s" % k)
            args.append(str(v))
        serverProcess = Popen(
            executable=executable,
            args=args,
            cwd=cwd if cwd else self.binDir(),
            stdout=fileno,
            stderr=fileno
        )
        return serverProcess
