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

    def testRepositories(self):
        self.assertEquals([], list(self.env.getRepositories()))
        repository = self.env.addRepository(name="test", baseUrl="test", metadataPrefix="test", setSpec="test", active=True, apiKey="inspiration")
        repositories = list(self.env.getRepositories())
        self.assertEquals([repository], repositories)


