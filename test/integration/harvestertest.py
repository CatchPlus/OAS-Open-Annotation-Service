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

from lxml.etree import tostring
from uuid import uuid4
from urllib import urlencode
from os.path import join, isdir
from os import makedirs

from oas.namespaces import xpath
from subprocess import Popen

from seecr.test.utils import getRequest, postRequest
from seecr.test.integrationtestcase import IntegrationTestCase

from oas.harvester.harvester import process
from oas.harvester import Environment

class HarvesterTest(IntegrationTestCase):

    def testOne(self):
        env = Environment(root=self.harvesterDataDir)
        open(join(self.httpDataDir, 'oai-repo1'), 'w').write(REPO1_RECORD)
        env.addRepository(name="repo-1", 
            baseUrl="http://localhost:%s/oai-repo1" % self.httpPortNumber, 
            metadataPrefix="rdf", 
            setSpec="aset", 
            active=True, 
            apiKey=self.apiKeyForTestUser)
        open(join(self.httpDataDir, 'oai-repo2'), 'w').write(REPO2_RECORD)
        env.addRepository(name="repo-2", 
            baseUrl="http://localhost:%s/oai-repo2" % self.httpPortNumber, 
            metadataPrefix="rdf", 
            active=False, 
            apiKey=self.apiKeyForAnotherTestUser)

        self.assertQuery(0, "repo1")
        self.assertQuery(0, "repo2")
        process(self.config) 
        self.assertQuery(1, "repo1")
        self.assertQuery(0, "repo2")

    def testInvalidUrl(self):
        env = Environment(root=self.harvesterDataDir)
        repository = env.addRepository(name="repo-1", 
            baseUrl="http://some.weird.url.that.does.not.work",
            metadataPrefix="rdf", 
            setSpec="aset", 
            active=True, 
            apiKey=self.apiKeyForTestUser)
        process(self.config) 
        self.assertEquals("<urlopen error [Errno -2] Name or service not known>", open(repository.errorLogPath).readlines()[-1])
       
    def testAddDelete(self):
        env = Environment(root=self.harvesterDataDir)
        open(join(self.httpDataDir, 'oai-testAddDelete'), 'w').write(TESTADDDELETE_ADD)

        repo = env.addRepository(name="repo-addDelete", 
            baseUrl="http://localhost:%s/oai-testAddDelete" % self.httpPortNumber, 
            metadataPrefix="rdf", 
            setSpec="aset", 
            active=True, 
            apiKey=self.apiKeyForTestUser)
        self.assertTrue(repo.active)

        self.assertQuery(0, "testAddDelete")
        process(self.config) 

        repo = env.getRepository(name=repo.name)  # reload for state change
        self.assertFalse(repo.active)
        repo.active = True
        repo.save()
        self.assertQuery(1, "testAddDelete")

        open(join(self.httpDataDir, 'oai-testAddDelete'), 'w').write(TESTADDDELETE_DELETE)
        process(self.config) 
        self.assertQuery(0, "testAddDelete")

    def assertQuery(self, count, query):
        headers, body = getRequest(self.portNumber, "/sru", arguments=dict(
            version="1.1", operation="searchRetrieve", query=query), parse='lxml')
        recordCount = int(xpath(body, '/srw:searchRetrieveResponse/srw:numberOfRecords/text()')[0])
        if recordCount != count:
            print tostring(body)
        self.assertEquals(count, recordCount)

        
TESTADDDELETE_ADD = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH 
    xmlns="http://www.openarchives.org/OAI/2.0/" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
    <responseDate>2012-05-02T09:09:35Z</responseDate>
    <request metadataPrefix="rdf" verb="ListRecords">http://oas.dev.seecr.nl:8000/oai</request>
    <ListRecords>
        <record>
            <header>
                <identifier>oai:oas.dev.seecr.nl:http://oas.dev.seecr.nl:8000/resolve/urn%3Auuid%3Ab5b05c7d-371f-4927-b0b1-ff9d3b4e2468</identifier>
                <datestamp>2012-04-24T09:37:39Z</datestamp>
                <setSpec>fietsventiel</setSpec>
            </header>
            <metadata>
                <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" rdf:about="http://oas.dev.seecr.nl:8000/resolve/urn%3Auuid%3Ab5b05c7d-371f-4927-b0b1-ff9d3b4e2468">
                        <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">testAddDelete</dc:title>
                    </oac:Annotation>
                </rdf:RDF>
            </metadata>
        </record>
    </ListRecords>
</OAI-PMH>"""

TESTADDDELETE_DELETE = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH 
    xmlns="http://www.openarchives.org/OAI/2.0/" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
    <responseDate>2012-05-02T09:09:35Z</responseDate>
    <request metadataPrefix="rdf" verb="ListRecords">http://oas.dev.seecr.nl:8000/oai</request>
    <ListRecords>
        <record>
            <header status="deleted">
                <identifier>http://oas.dev.seecr.nl:8000/resolve/urn%3Auuid%3Ab5b05c7d-371f-4927-b0b1-ff9d3b4e2468</identifier>
                <datestamp>2012-04-24T09:37:39Z</datestamp>
                <setSpec>fietsventiel</setSpec>
            </header>
        </record>
    </ListRecords>
</OAI-PMH>"""

REPO1_RECORD = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH 
    xmlns="http://www.openarchives.org/OAI/2.0/" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
    <responseDate>2012-05-02T09:09:35Z</responseDate>
    <request metadataPrefix="rdf" verb="ListRecords">http://oas.dev.seecr.nl:8000/oai</request>
    <ListRecords>
        <record>
            <header>
                <identifier>urn:repo:1:record</identifier>
                <datestamp>2012-04-24T09:37:39Z</datestamp>
                <setSpec>fietsventiel</setSpec>
            </header>
            <metadata>
                <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" rdf:about="http://oas.dev.seecr.nl:8000/resolve/urn%3Auuid%3Ab5b05c7d-371f-4927-b0b1-ff9d3b4e2468">
                        <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">repo1</dc:title>
                    </oac:Annotation>
                </rdf:RDF>
            </metadata>
        </record>
    </ListRecords>
</OAI-PMH>"""

REPO2_RECORD = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH 
    xmlns="http://www.openarchives.org/OAI/2.0/" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
    <responseDate>2012-05-02T09:09:35Z</responseDate>
    <request metadataPrefix="rdf" verb="ListRecords">http://oas.dev.seecr.nl:8000/oai</request>
    <ListRecords>
        <record>
            <header>
                <identifier>urn:repo:2:record</identifier>
                <datestamp>2012-04-24T09:37:39Z</datestamp>
                <setSpec>fietsventiel</setSpec>
            </header>
            <metadata>
                <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                    <oac:Annotation xmlns:oac="http://www.openannotation.org/ns/" rdf:about="http://oas.dev.seecr.nl:8000/resolve/urn%3Auuid%3Ab5b05c7d-371f-4927-b0b1-ff9d3b4e2468">
                        <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">repo2</dc:title>
                    </oac:Annotation>
                </rdf:RDF>
            </metadata>
        </record>
    </ListRecords>
</OAI-PMH>"""
