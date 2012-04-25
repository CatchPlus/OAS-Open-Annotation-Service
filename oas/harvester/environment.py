from simplejson import dump as jsonSave, load as jsonLoad

from os.path import join, isfile, isdir
from os import makedirs, rename, listdir
from shutil import rmtree

CONFIG_FILENAME = 'config.json'

class Environment(object):
    def __init__(self, root):
        self._root = root
        if not isdir(self._root):
            makedirs(self._root)

    def getRepositories(self):
        for name in listdir(self._root):
            yield self.getRepository(name)

    def addRepository(self, name, **kwargs):
        repository = Repository(name=name, **kwargs)
        repository.saveIn(self._root)
        return repository

    def deleteRepository(self, name):
        self.getRepository(name).delete(self._root)

    def getRepository(self, name):
        return Repository.read(self._root, name)

class Repository(object):
    def __init__(self, name, baseUrl='', metadataPrefix='', setSpec='', active=False, apiKey=''):
        self.name = name
        self.baseUrl = baseUrl
        self.metadataPrefix = metadataPrefix
        self.setSpec = setSpec
        self.active = active
        self.apiKey = apiKey

    def saveIn(self, directory):
        directoryName = join(directory, self.name)
        if not isdir(directoryName):
            makedirs(directoryName)

        configFile = join(directoryName, CONFIG_FILENAME)
        tmpFile = '%s.tmp' % configFile
        jsonSave({
            'name': self.name,
            'baseUrl': self.baseUrl,
            'metadataPrefix': self.metadataPrefix,
            'setSpec': self.setSpec,
            'active': self.active,
            'apiKey': self.apiKey,
            },
            open(tmpFile, 'w'))
        rename(tmpFile, configFile)

    def delete(self, directory):
        rmtree(join(directory, self.name))

    @staticmethod
    def read(directory, name):
        jsonData = jsonLoad(open(join(directory, name, CONFIG_FILENAME)))
        return Repository(
            name=jsonData['name'],
            baseUrl=jsonData['baseUrl'],
            metadataPrefix=jsonData['metadataPrefix'],
            setSpec=jsonData['setSpec'],
            active=jsonData['active'],
            apiKey=jsonData['apiKey']
        )

    def __eq__(self, other):
        return self.name == other.name and \
            self.baseUrl == other.baseUrl and \
            self.metadataPrefix == other.metadataPrefix and \
            self.setSpec == other.setSpec and \
            self.active == other.active and \
            self.apiKey == other.apiKey

