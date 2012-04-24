from simplejson import dump as jsonSave, load as jsonLoad

from os.path import join, isfile, isdir
from os import makedirs, rename, listdir

CONFIG_FILENAME = 'config.json'

class Environment(object):
    def __init__(self, root):
        self._root = root

    def getRepositories(self):
        for name in listdir(self._root):
            yield self.getRepository(name)

    def addRepository(self, repository):
        repository.saveIn(self._root)

    def getRepository(self, name):
        return Repository.read(self._root, name)

class Repository(object):
    def __init__(self, name, baseUrl, metadataPrefix, setSpec, active, apiKey):
        self._name = name
        self._baseUrl = baseUrl
        self._metadataPrefix = metadataPrefix
        self._setSpec = setSpec
        self._active = active
        self._apiKey = apiKey

    def saveIn(self, directory):
        directoryName = join(directory, self._name)
        if not isdir(directoryName):
            makedirs(directoryName)

        configFile = join(directoryName, CONFIG_FILENAME)
        tmpFile = '%s.tmp' % configFile
        jsonSave({
            'name': self._name,
            'baseUrl': self._baseUrl,
            'metadataPrefix': self._metadataPrefix,
            'setSpec': self._setSpec,
            'active': self._active,
            'apiKey': self._apiKey,
            },
            open(tmpFile, 'w'))
        rename(tmpFile, configFile)

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
        return self._name == other._name and \
            self._baseUrl == other._baseUrl and \
            self._metadataPrefix == other._metadataPrefix and \
            self._setSpec == other._setSpec and \
            self._active == other._active and \
            self._apiKey == other._apiKey

