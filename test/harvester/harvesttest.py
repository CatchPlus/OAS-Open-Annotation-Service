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

from seecr.test import SeecrTestCase, CallTrace
from weightless.core import be
from meresco.core import Observable
from testutil import lico
from StringIO import StringIO

from oas.harvester import Harvest, Environment

class HarvestTest(SeecrTestCase):

    def setUp(self):
        SeecrTestCase.setUp(self)
        self.observer = CallTrace(emptyGeneratorMethods=['add', 'delete'])
        self.harvest = Harvest()
        self.dna = be(
            (Observable(),
                (self.harvest,
                    (self.observer, )
                )
            )
        )

    def testAddDeleteWithResumption(self):
        env = Environment(root=self.tempdir)
        repository = env.addRepository(name="test", active=True)

        self.harvest._urlopen = lambda url: StringIO(OAIPMH_OUTPUT % '<resumptionToken>TheResumptionToken</resumptionToken>')

        lico(self.dna.all.process(repository))
        self.assertEquals(['add', 'delete'], [m.name for m in self.observer.calledMethods])
        self.assertEquals('TheResumptionToken', repository.resumptionToken)
        self.assertTrue(repository.active)
        
    def testAddDeleteWithoutResumption(self):
        env = Environment(root=self.tempdir)
        repository = env.addRepository(name="test", active=True)

        self.harvest._urlopen = lambda url: StringIO(OAIPMH_OUTPUT)

        lico(self.dna.all.process(repository))
        self.assertEquals(['add', 'delete'], [m.name for m in self.observer.calledMethods])
        self.assertEquals('', repository.resumptionToken)
        self.assertFalse(repository.active)

    def testLogError(self):
        env = Environment(root=self.tempdir)
        repository = env.addRepository(name="test", active=True)

        self.harvest._urlopen = lambda url: StringIO(OAIPMH_ERROR_OUTPUT)

        lico(self.dna.all.process(repository))
        self.assertEquals('errorCode: error text', repository.readErrorLog())



OAIPMH_OUTPUT = """<?xml version="1.0" encoding="UTF-8"?>
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
            </header>
            <metadata><xml/></metadata>
        </record>
        <record>
            <header status="deleted">
                <identifier>urn:repo:2:record</identifier>
                <datestamp>2012-04-24T09:37:39Z</datestamp>
            </header>
            <metadata><xml/></metadata>
        </record>
        %s
    </ListRecords>
</OAI-PMH>"""

        
OAIPMH_ERROR_OUTPUT = """<?xml version="1.0" encoding="UTF-8"?>
<OAI-PMH 
    xmlns="http://www.openarchives.org/OAI/2.0/" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:schemaLocation="http://www.openarchives.org/OAI/2.0/ http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd">
    <responseDate>2012-05-02T09:09:35Z</responseDate>
    <request metadataPrefix="rdf" verb="ListRecords">http://oas.dev.seecr.nl:8000/oai</request>
    <error code="errorCode">error text</error>
</OAI-PMH>"""
