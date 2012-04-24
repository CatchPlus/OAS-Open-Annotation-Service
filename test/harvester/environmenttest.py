from seecr.test import SeecrTestCase

from os.path import join, isfile
from oas.harvester import Repository, Environment

class EnvironmentTest(SeecrTestCase):
    
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.env = Environment(root=self.tempdir)

    def testWriteFile(self):
        repo = Repository(
            name="example_repo", 
            baseUrl="http://example.org/oai", 
            metadataPrefix="oai_dc", 
            setSpec="aset", 
            active=True, 
            apiKey="an api key"
        )
        self.assertFalse(isfile(join(self.env._root, repo._name, 'config.json')))
        self.env.addRepository(repo)
        self.assertTrue(isfile(join(self.env._root, repo._name, 'config.json')))

    def testGetReadFile(self):
        repo = Repository(
            name="example_repo", 
            baseUrl="http://example.org/oai", 
            metadataPrefix="oai_dc", 
            setSpec="aset", 
            active=True, 
            apiKey="an api key"
        )
        self.env.addRepository(repo)
        repo2 = self.env.getRepository(name='example_repo')

        self.assertEquals(repo, repo2)

    def testRepositories(self):
        self.assertEquals([], list(self.env.getRepositories()))
        repository = Repository(name="test", baseUrl="test", metadataPrefix="test", setSpec="test", active=True, apiKey="inspiration")
        self.env.addRepository(repository)
        repositories = list(self.env.getRepositories())
        self.assertEquals([repository], repositories)


