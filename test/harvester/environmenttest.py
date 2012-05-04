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

from seecr.test import SeecrTestCase

from os.path import join, isfile, isdir
from oas.harvester import Repository, Environment

class EnvironmentTest(SeecrTestCase):
    
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.env = Environment(root=join(self.tempdir, 'db'))

    def testCreateDir(self):
        self.assertTrue(isdir(self.env._root))

    def testWriteFile(self):
        self.assertFalse(isfile(join(self.env._root, "example_repo", 'config.json')))
        self.env.addRepository(name="example_repo", baseUrl="http://example.org/oai", metadataPrefix="oai_dc", setSpec="aset", active=True, apiKey="an api key")
        self.assertTrue(isfile(join(self.env._root, "example_repo", 'config.json')))

    def testGetReadFile(self):
        repo = self.env.addRepository(name="example_repo", baseUrl="http://example.org/oai", metadataPrefix="oai_dc", setSpec="aset", active=True, apiKey="an api key")
        repo2 = self.env.getRepository(name='example_repo')

        self.assertEquals(repo, repo2)
        self.assertEquals(repo.active, repo2.active)

    def testRepositories(self):
        self.assertEquals([], list(self.env.getRepositories()))
        repository = self.env.addRepository(name="test", baseUrl="test", metadataPrefix="test", setSpec="test", active=True, apiKey="inspiration")
        repositories = list(self.env.getRepositories())
        self.assertEquals([repository], repositories)

    def testDefaultValues(self):
        repository = self.env.addRepository(name="test")
        self.assertEquals('', repository.baseUrl)
        self.assertEquals('', repository.metadataPrefix)
        self.assertEquals('', repository.setSpec)
        self.assertEquals('', repository.apiKey)
        self.assertEquals(False, repository.active)

    def testDeleteRepository(self):
        repository = self.env.addRepository(name="test")
        repositories = list(self.env.getRepositories())
        self.assertEquals([repository], repositories)
        self.env.deleteRepository(name="test")
        repositories = list(self.env.getRepositories())
        self.assertEquals([], repositories)

    def testHarvestStatePersistent(self):
        repository = self.env.addRepository(name='test')
        repository.resumptionToken = 'xyz'
        repository.save()
        repositoryRevisited = self.env.getRepository(name='test')
        self.assertEquals('xyz', repositoryRevisited.resumptionToken)




